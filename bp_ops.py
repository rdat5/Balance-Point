import bpy
from math import radians
from .utils import is_valid_triangle, get_triangle_normal, get_moment_of_inertia, projectile_position
from mathutils import Vector

class ToggleDrawing(bpy.types.Operator):
    """Adds/Removes center of mass render function from draw handler"""
    bl_idname = "balance_point.toggle_drawing"
    bl_label = "Toggle Drawing"

    def execute(self, context):
        com_props = context.scene.com_properties

        com_props.com_drawing_on = not com_props.com_drawing_on
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        return {'FINISHED'}

class AddMassObjectGroup(bpy.types.Operator):
    """Adds a new Mass Object Group"""
    bl_idname = "balance_point.massgroup_add"
    bl_label = "Add new Mass Object Group"

    def execute(self, context):
        new_item = bpy.context.scene.bp_mass_object_groups.add()
        new_item.name = f"Mass Object Group {len(bpy.context.scene.bp_mass_object_groups)}"
        return {'FINISHED'}


class RemoveMassObjectGroup(bpy.types.Operator):
    """Adds a new Mass Object Group"""
    bl_idname = "balance_point.massgroup_remove"
    bl_label = "Remove last Mass Object Group"

    @classmethod
    def poll(cls, context):
        bp_mass_groups = context.scene.bp_mass_object_groups

        return len(bp_mass_groups) > 0

    def execute(self, context):
        if len(bpy.context.scene.bp_mass_object_groups) > 0:
            bpy.context.scene.bp_mass_object_groups.remove(len(bpy.context.scene.bp_mass_object_groups) - 1)
        return {'FINISHED'}


class SetReferencePoint(bpy.types.Operator):
    """Sets the coordinate of a reference point."""
    bl_idname = "balance_point.referencepoint_set"
    bl_label = "Set Reference Point From 3D Cursor"

    target: bpy.props.IntProperty(name="Reference point being set.")

    def execute(self, context):
        physics_props = context.scene.bp_physics_properties
        sel_mog = context.scene.bp_mass_object_groups[physics_props.selected_mog]

        cursor_loc = context.scene.cursor.location
        cursor_coords = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

        match self.target:
            case 1:
                physics_props.align_rotation_p1 = cursor_coords
            case 2: 
                physics_props.align_rotation_p2 = cursor_coords
            case 3:
                physics_props.ballistics_p0 = sel_mog.com_object.matrix_world.translation
                physics_props.ballistics_p1 = cursor_coords
        return {'FINISHED'}


class AlignAxisByPoints(bpy.types.Operator):
    """Aligns COM Object's rotation axis about two reference points."""
    bl_idname = "balance_point.align_axis"
    bl_label = "Align COM Object's Axis"

    @classmethod
    def poll(cls, context):
        physics_props = context.scene.bp_physics_properties
        sel_mog = context.scene.bp_mass_object_groups[physics_props.selected_mog]

        p1 = physics_props.align_rotation_p1
        p2 = physics_props.align_rotation_p2
        p3 = sel_mog.com_object.matrix_world.translation
        return is_valid_triangle(p1, p2, p3)

    def execute(self, context):
        physics_props = context.scene.bp_physics_properties
        com_obj = context.scene.bp_mass_object_groups[physics_props.selected_mog].com_object

        p1 = physics_props.align_rotation_p1
        p2 = physics_props.align_rotation_p2
        p3 = com_obj.matrix_world.translation
        norm = get_triangle_normal(p1, p2, p3)
        com_obj.rotation_axis_angle[1] = norm[0]
        com_obj.rotation_axis_angle[2] = norm[1]
        com_obj.rotation_axis_angle[3] = norm[2]
        return {'FINISHED'}


class SetInitialMomentOfInertia(bpy.types.Operator):
    """Sets the initial moment of inertia to be used for physics baking."""
    bl_idname = "balance_point.set_angular_values"
    bl_label = "Set Initial Moment of Inertia"

    def execute(self, context):
        physics_props = context.scene.bp_physics_properties
        sel_mog = context.scene.bp_mass_object_groups[physics_props.selected_mog]

        physics_props.initial_moment_of_inertia = sel_mog.moment_of_inertia
        return {'FINISHED'}


class BakeBPPhysics(bpy.types.Operator):
    """Bakes the rotation and ballistics curve for the given range."""
    bl_idname = "balance_point.bake_physics"
    bl_label = "Bake Physics"

    @classmethod
    def poll(cls, context):
        physics_props = context.scene.bp_physics_properties
        sel_mog = context.scene.bp_mass_object_groups[physics_props.selected_mog]

        if physics_props.frame_end <= physics_props.frame_start:
            return False

        return True


    def execute(self, context):
        physics_props = context.scene.bp_physics_properties
        sel_mog = context.scene.bp_mass_object_groups[physics_props.selected_mog]

        angle = 0

        physics_props.ballistics_p0 = sel_mog.com_object.matrix_world.translation
        p0 = physics_props.ballistics_p0
        p1 = physics_props.ballistics_p1

        for f in range(physics_props.frame_start, physics_props.frame_end + 1):
            bpy.context.scene.frame_set(f)
            
            # Rotation
            sel_mog.com_object.rotation_axis_angle[0] = radians(angle)

            sel_mog.com_object.keyframe_insert(data_path='rotation_axis_angle', index=0, keytype='GENERATED')

            current_axis = Vector((sel_mog.com_object.rotation_axis_angle[1], sel_mog.com_object.rotation_axis_angle[2], sel_mog.com_object.rotation_axis_angle[3]))
            current_moment_of_inertia = get_moment_of_inertia(sel_mog.mass_object_collection.all_objects, sel_mog.com_location, current_axis)
            angle += physics_props.initial_angular_velocity * (physics_props.initial_moment_of_inertia / current_moment_of_inertia)
        
            # Ballistics
            start_pos = (p0[0], p0[1], p0[2])
            ref_pos = (p1[0], p1[1], p1[2])
            gravity = physics_props.gravity
            time_of_flight = float(physics_props.time_of_flight)
            elapsed_time = float(f - physics_props.frame_start) / physics_props.frame_rate

            point_position = projectile_position(start_pos, ref_pos, gravity, time_of_flight, elapsed_time)

            sel_mog.com_object.matrix_world.translation = point_position
            sel_mog.com_object.keyframe_insert(data_path='location', keytype='GENERATED')

        return {'FINISHED'}