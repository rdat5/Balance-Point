import bpy
from math import radians
from .utils import is_valid_triangle, get_triangle_normal, get_moment_of_inertia, projectile_position, get_com
from mathutils import Vector

class ToggleDrawing(bpy.types.Operator):
    """Adds/Removes center of mass render function from draw handler"""
    bl_idname = "balance_point.toggle_drawing"
    bl_label = "Toggle Drawing"

    def execute(self, context):
        com_props = context.scene.com_properties

        com_props.com_drawing_on = not com_props.com_drawing_on
        bpy.context.region.tag_redraw()
        return {'FINISHED'}

class AddMassObjectGroup(bpy.types.Operator):
    """Adds a new Mass Object Group"""
    bl_idname = "balance_point.massgroup_add"
    bl_label = "Add new Mass Object Group"

    def execute(self, context):
        scene = context.scene

        def get_unique_name(base_name, collection):
            existing_names = {item.name for item in collection}
            unique_name = base_name
            suffix = 1
            while unique_name in existing_names:
                unique_name = f"{base_name}.{suffix:03}"
                suffix += 1
            return unique_name

        new_item = bpy.context.scene.bp_mass_object_groups.add()
        new_name = get_unique_name("Mass Object Group {:d}".format(len(scene.bp_mass_object_groups)), scene.bp_mass_object_groups)
        new_item.name = new_name
        return {'FINISHED'}


class RemoveMassObjectGroup(bpy.types.Operator):
    """Removes a new Mass Object Group"""
    bl_idname = "balance_point.massgroup_remove"
    bl_label = "Remove selected Mass Object Group"

    @classmethod
    def poll(cls, context):
        scene = context.scene
        mass_object_groups = scene.bp_mass_object_groups
        selected_index = scene.bp_group_index
        return selected_index < len(mass_object_groups)

    def execute(self, context):
        scene = context.scene
        index = scene.bp_group_index
        scene.bp_mass_object_groups.remove(index)
        scene.bp_group_index = max(0, index - 1)
        return {'FINISHED'}


class SetReferencePoint(bpy.types.Operator):
    """Sets the coordinate of a reference point."""
    bl_idname = "balance_point.referencepoint_set"
    bl_label = "Set Reference Point From 3D Cursor"

    # target: bpy.props.IntProperty(name="Reference point being set.")

    def execute(self, context):
        physics_props = context.scene.bp_physics_properties
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        cursor_loc = context.scene.cursor.location
        cursor_coords = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

        # match self.target:
        #     case 1:
        #         physics_props.align_rotation_p1 = cursor_coords
        #     case 2: 
        #         physics_props.align_rotation_p2 = cursor_coords
        #     case 3:
        #         physics_props.ballistics_p0 = sel_mog.com_object.matrix_world.translation
        #         physics_props.ballistics_p1 = cursor_coords

        sel_mog.reference_point = cursor_coords
        
        bpy.context.region.tag_redraw()
        return {'FINISHED'}


class SetStartingPoint(bpy.types.Operator):
    """Sets the coordinate of a ballistics starting point."""
    bl_idname = "balance_point.startingpoint_set"
    bl_label = "Set Starting Point From 3D Cursor"

    # target: bpy.props.IntProperty(name="Reference point being set.")

    def execute(self, context):
        physics_props = context.scene.bp_physics_properties
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        cursor_loc = context.scene.cursor.location
        cursor_coords = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

        # match self.target:
        #     case 1:
        #         physics_props.align_rotation_p1 = cursor_coords
        #     case 2: 
        #         physics_props.align_rotation_p2 = cursor_coords
        #     case 3:
        #         physics_props.ballistics_p0 = sel_mog.com_object.matrix_world.translation
        #         physics_props.ballistics_p1 = cursor_coords

        sel_mog.ballistics_starting_point = cursor_coords
        
        bpy.context.region.tag_redraw()
        return {'FINISHED'}


class SetStartingPointToCOM(bpy.types.Operator):
    """Sets the coordinate of a ballistics starting point to Pinned Rig's center of mass."""
    bl_idname = "balance_point.startingpointcom_set"
    bl_label = "Set Starting Point From Pinned Rig's Center of Mass"

    @classmethod
    def poll(cls, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        if sel_mog.mass_object_collection is None:
            False

        return True

    def execute(self, context):
        physics_props = context.scene.bp_physics_properties
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        # cursor_loc = context.scene.cursor.location
        # cursor_coords = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

        sel_mog.ballistics_starting_point = get_com(sel_mog.mass_object_collection.all_objects)
        
        bpy.context.region.tag_redraw()
        return {'FINISHED'}


class AlignAxisByPoints(bpy.types.Operator):
    """Aligns pinned rig's rotation axis to face the reference point."""
    bl_idname = "balance_point.align_axis"
    bl_label = "Align Axis to Reference Point"

    @classmethod
    def poll(cls, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        rig_com = get_com(sel_mog.mass_object_collection.all_objects)

        p1 = sel_mog.reference_point
        p2 = [sel_mog.reference_point[0], sel_mog.reference_point[1], sel_mog.reference_point[2] + 1]
        p3 = [rig_com[0], rig_com[1], rig_com[2]]
        return is_valid_triangle(p1, p2, p3)

    def execute(self, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        rig_com = get_com(sel_mog.mass_object_collection.all_objects)

        p1 = sel_mog.reference_point
        p2 = [sel_mog.reference_point[0], sel_mog.reference_point[1], sel_mog.reference_point[2] + 1]
        p3 = [rig_com[0], rig_com[1], rig_com[2]]
        norm = get_triangle_normal(p1, p2, p3)
        sel_mog.pinned_rig.rotation_axis_angle[1] = norm[0]
        sel_mog.pinned_rig.rotation_axis_angle[2] = norm[1]
        sel_mog.pinned_rig.rotation_axis_angle[3] = norm[2]
        return {'FINISHED'}


class AlignAxisByCursor(bpy.types.Operator):
    """Aligns pinned rig's rotation axis to face the 3D Cursor."""
    bl_idname = "balance_point.align_axis_cursor"
    bl_label = "Align Axis to 3D Cursor"

    @classmethod
    def poll(cls, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        rig_com = get_com(sel_mog.mass_object_collection.all_objects)
        cursor = context.scene.cursor.location

        p1 = cursor
        p2 = [cursor[0], cursor[1], cursor[2] + 1]
        p3 = [rig_com[0], rig_com[1], rig_com[2]]
        return is_valid_triangle(p1, p2, p3)

    def execute(self, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        rig_com = get_com(sel_mog.mass_object_collection.all_objects)
        cursor = context.scene.cursor.location

        p1 = cursor
        p2 = [cursor[0], cursor[1], cursor[2] + 1]
        p3 = [rig_com[0], rig_com[1], rig_com[2]]
        norm = get_triangle_normal(p1, p2, p3)
        sel_mog.pinned_rig.rotation_axis_angle[1] = norm[0]
        sel_mog.pinned_rig.rotation_axis_angle[2] = norm[1]
        sel_mog.pinned_rig.rotation_axis_angle[3] = norm[2]
        return {'FINISHED'}


class CalculateAnglePreview(bpy.types.Operator):
    """Calculates and stores Moment of Inertia for the given range."""
    bl_idname = "balance_point.calculate_angle_preview"
    bl_label = "Calculate Angle Preview"

    @classmethod
    def poll(cls, context):
        physics_props = context.scene.bp_physics_properties

        if physics_props.frame_end <= physics_props.frame_start:
            return False

        return True

    def execute(self, context):
        physics_props = context.scene.bp_physics_properties
        sel_mog = context.scene.bp_mass_object_groups[physics_props.selected_mog]
        mois = physics_props.calculated_mois

        mois.clear()

        # For returning to original frame after operation
        original_frame = bpy.context.scene.frame_current

        # Get Center of Mass
        group_com = get_com(sel_mog.mass_object_collection.all_objects)

        bpy.context.scene.frame_set(physics_props.frame_start)
        angle = sel_mog.com_object.rotation_axis_angle[0]
        current_axis = Vector((sel_mog.com_object.rotation_axis_angle[1], sel_mog.com_object.rotation_axis_angle[2], sel_mog.com_object.rotation_axis_angle[3]))
        initial_moment_of_inertia = get_moment_of_inertia(sel_mog.mass_object_collection.all_objects, group_com, current_axis)

        for f in range(physics_props.frame_start, physics_props.frame_end + 1):
            bpy.context.scene.frame_set(f)

            current_moment_of_inertia = get_moment_of_inertia(sel_mog.mass_object_collection.all_objects, group_com, current_axis)

            new_moi = mois.add()
            new_moi.angle = angle
            new_moi.moment_of_inertia = get_moment_of_inertia(sel_mog.mass_object_collection.all_objects, group_com, current_axis)
            angle += physics_props.initial_angular_velocity * (initial_moment_of_inertia / current_moment_of_inertia)
        
        bpy.context.scene.frame_set(original_frame)
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

        # Get Center of Mass
        group_com = get_com(sel_mog.mass_object_collection.all_objects)

        physics_props.ballistics_p0 = group_com
        p0 = physics_props.ballistics_p0
        p1 = physics_props.ballistics_p1

        # For returning to original frame after operation
        original_frame = bpy.context.scene.frame_current

        bpy.context.scene.frame_set(physics_props.frame_start)
        angle = sel_mog.com_object.rotation_axis_angle[0]
        current_axis = Vector((sel_mog.com_object.rotation_axis_angle[1], sel_mog.com_object.rotation_axis_angle[2], sel_mog.com_object.rotation_axis_angle[3]))

        initial_moment_of_inertia = get_moment_of_inertia(sel_mog.mass_object_collection.all_objects, group_com, current_axis)

        for f in range(physics_props.frame_start, physics_props.frame_end + 1):
            bpy.context.scene.frame_set(f)
            
            # Rotation
            sel_mog.com_object.rotation_axis_angle[0] = radians(angle)

            sel_mog.com_object.keyframe_insert(data_path='rotation_axis_angle', keytype='GENERATED')

            current_moment_of_inertia = get_moment_of_inertia(sel_mog.mass_object_collection.all_objects, group_com, current_axis)
            angle += physics_props.initial_angular_velocity * (initial_moment_of_inertia / current_moment_of_inertia)
        
            # Ballistics
            start_pos = (p0[0], p0[1], p0[2])
            ref_pos = (p1[0], p1[1], p1[2])
            gravity = physics_props.gravity
            time_of_flight = float(physics_props.time_of_flight)
            elapsed_time = float(f - physics_props.frame_start) / physics_props.frame_rate

            point_position = projectile_position(start_pos, ref_pos, gravity, time_of_flight, elapsed_time)

            sel_mog.com_object.matrix_world.translation = point_position
            sel_mog.com_object.keyframe_insert(data_path='location', keytype='GENERATED')
        
        bpy.context.scene.frame_set(original_frame)

        return {'FINISHED'}