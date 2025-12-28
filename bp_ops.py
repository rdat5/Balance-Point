import bpy
from math import radians
from .utils import (
    is_valid_triangle,
    get_triangle_normal,
    get_inertia_tensor,
    projectile_position,
    get_com
)
from mathutils import Vector, Matrix, Quaternion


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
                unique_name = "{}.{:03}".format(base_name, suffix)
                suffix += 1
            return unique_name

        new_item = bpy.context.scene.bp_mass_object_groups.add()
        new_name = get_unique_name("Mass Object Group {:d}".format(
            len(scene.bp_mass_object_groups)), scene.bp_mass_object_groups)
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

    def execute(self, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        cursor_loc = context.scene.cursor.location
        cursor_coords = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

        sel_mog.reference_point = cursor_coords

        bpy.context.region.tag_redraw()
        return {'FINISHED'}


class SetReferencePointToCOM(bpy.types.Operator):
    """Sets the coordinate of ballistics reference point to Pinned Rig's center of mass."""
    bl_idname = "balance_point.referencepointcom_set"
    bl_label = "Set Reference Point To Pinned Rig's Center of Mass"

    @classmethod
    def poll(cls, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        if sel_mog.mass_object_collection is None:
            False

        return True

    def execute(self, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        sel_mog.reference_point = get_com(
            sel_mog.mass_object_collection.all_objects)

        bpy.context.region.tag_redraw()
        return {'FINISHED'}


class SetStartingPoint(bpy.types.Operator):
    """Sets the coordinate of the ballistics starting point."""
    bl_idname = "balance_point.startingpoint_set"
    bl_label = "Set Starting Point From 3D Cursor"

    def execute(self, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        cursor_loc = context.scene.cursor.location
        cursor_coords = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

        sel_mog.ballistics_starting_point = cursor_coords

        bpy.context.region.tag_redraw()
        return {'FINISHED'}


class SetStartingPointToCOM(bpy.types.Operator):
    """Sets the coordinate of the ballistics starting point to Pinned Rig's center of mass."""
    bl_idname = "balance_point.startingpointcom_set"
    bl_label = "Set Starting Point From Pinned Rig's Center of Mass"

    @classmethod
    def poll(cls, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        if sel_mog.mass_object_collection is None:
            False

        return True

    def execute(self, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        sel_mog.ballistics_starting_point = get_com(
            sel_mog.mass_object_collection.all_objects)

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
        p2 = [sel_mog.reference_point[0], sel_mog.reference_point[1],
              sel_mog.reference_point[2] + 1]
        p3 = [rig_com[0], rig_com[1], rig_com[2]]
        return is_valid_triangle(p1, p2, p3)

    def execute(self, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        rig_com = get_com(sel_mog.mass_object_collection.all_objects)

        p1 = sel_mog.reference_point
        p2 = [sel_mog.reference_point[0], sel_mog.reference_point[1],
              sel_mog.reference_point[2] + 1]
        p3 = [rig_com[0], rig_com[1], rig_com[2]]
        norm = get_triangle_normal(p3, p2, p1)
        sel_mog.initial_axis.x = norm[0]
        sel_mog.initial_axis.y = norm[1]
        sel_mog.initial_axis.z = norm[2]
        bpy.context.region.tag_redraw()
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
        norm = get_triangle_normal(p3, p2, p1)
        sel_mog.initial_axis.x = norm[0]
        sel_mog.initial_axis.y = norm[1]
        sel_mog.initial_axis.z = norm[2]
        bpy.context.region.tag_redraw()
        return {'FINISHED'}


class AlignAxisByCursorRef(bpy.types.Operator):
    """Aligns pinned rig's rotation axis according to 3D Cursor and Reference Point."""
    bl_idname = "balance_point.align_axis_cursor_ref"
    bl_label = "Align Axis to 3D Cursor and Reference Point"

    @classmethod
    def poll(cls, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        rig_com = get_com(sel_mog.mass_object_collection.all_objects)
        cursor = context.scene.cursor.location

        p1 = cursor
        p2 = sel_mog.reference_point
        p3 = [rig_com[0], rig_com[1], rig_com[2]]

        return is_valid_triangle(p1, p2, p3)

    def execute(self, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        rig_com = get_com(sel_mog.mass_object_collection.all_objects)
        cursor = context.scene.cursor.location

        p1 = cursor
        p2 = sel_mog.reference_point
        p3 = [rig_com[0], rig_com[1], rig_com[2]]
        norm = get_triangle_normal(p3, p2, p1)
        sel_mog.initial_axis.x = norm[0]
        sel_mog.initial_axis.y = norm[1]
        sel_mog.initial_axis.z = norm[2]
        bpy.context.region.tag_redraw()
        return {'FINISHED'}


class BakeBPPhysics(bpy.types.Operator):
    """Bakes the rotation and ballistics curve for the given range."""
    bl_idname = "balance_point.bake_physics"
    bl_label = "Bake Physics"

    @classmethod
    def poll(cls, context):
        physics_props = context.scene.bp_physics_properties
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        if physics_props.frame_end <= physics_props.frame_start:
            return False

        if not (sel_mog.pin_xyz[0] == True and sel_mog.pin_xyz[1] == True and sel_mog.pin_xyz[2] == True):
            return False

        if sel_mog.pinned_rig.pose.bones[sel_mog.root_bone] is None:
            return False

        return True

    def execute(self, context):
        physics_props = context.scene.bp_physics_properties
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]
        root_bone = sel_mog.pinned_rig.pose.bones[sel_mog.root_bone]

        # For returning to original frame after operation
        original_frame = bpy.context.scene.frame_current

        bpy.context.scene.frame_set(physics_props.frame_start)

        # Get Center of Mass
        group_com = get_com(sel_mog.mass_object_collection.all_objects)

        I_start = get_inertia_tensor(sel_mog.mass_object_collection.all_objects, group_com)

        initial_axis = Vector((sel_mog.initial_axis.x, sel_mog.initial_axis.y, sel_mog.initial_axis.z))

        omega_start = initial_axis * physics_props.initial_angular_velocity

        L_vector = I_start @ omega_start

        p0 = sel_mog.ballistics_starting_point
        p1 = sel_mog.reference_point

        dt = 1.0 / context.scene.render.fps

        for f in range(physics_props.frame_start, physics_props.frame_end + 1):
            bpy.context.scene.frame_set(f)
            
            # Rotation
            current_quat = root_bone.rotation_quaternion.copy()
            if f > physics_props.frame_start:
                current_com = get_com(sel_mog.mass_object_collection.all_objects)
                
                I_current = get_inertia_tensor(sel_mog.mass_object_collection.all_objects, current_com)
                
                try:
                    I_inv = I_current.inverted()
                except ValueError:
                    I_inv = Matrix.Identity(3)
                    
                omega_new = I_inv @ L_vector

                rotation_speed = omega_new.length
                
                if rotation_speed > 1e-6:
                    rotation_axis = omega_new.normalized()
                    theta_step = rotation_speed * dt
                    
                    delta_quat = Quaternion(rotation_axis, theta_step)
                    
                    current_quat = delta_quat @ current_quat
                    current_quat.normalize()

            root_bone.rotation_quaternion = current_quat
            root_bone.keyframe_insert(data_path='rotation_quaternion', frame=f)

            # Ballistics
            start_pos = (p0[0], p0[1], p0[2])
            ref_pos = (p1[0], p1[1], p1[2])
            gravity = physics_props.gravity
            time_of_flight = float(physics_props.time_of_flight)
            elapsed_time = float(
                f - physics_props.frame_start) / physics_props.frame_rate

            point_position = projectile_position(
                start_pos, ref_pos, gravity, time_of_flight, elapsed_time)

            sel_mog.com_location = point_position
            context.scene.keyframe_insert(
                data_path="bp_mass_object_groups[{}].com_location".format(selected_index), keytype='GENERATED')

            sel_mog.is_rig_pinned = True
            context.scene.keyframe_insert(
                data_path="bp_mass_object_groups[{}].is_rig_pinned".format(selected_index), keytype='GENERATED', options={'INSERTKEY_NEEDED'})
            
            context.view_layer.update()

        # Return to original frame
        bpy.context.scene.frame_set(original_frame)

        return {'FINISHED'}


class CalculateBPMotionPath(bpy.types.Operator):
    """Calculate the motion path of the mass object group's center of mass for the given range."""
    bl_idname = "balance_point.calculate_com_motion_path"
    bl_label = "Calculate Center of Mass Motion Path"

    @classmethod
    def poll(cls, context):
        physics_props = context.scene.bp_physics_properties

        if physics_props.motion_path_frame_end <= physics_props.motion_path_frame_start:
            return False

        return True

    def execute(self, context):
        physics_props = context.scene.bp_physics_properties
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]
        motion_path_points = sel_mog.motion_path_points

        # Clear points
        motion_path_points.clear()

        # For returning to original frame after operation
        original_frame = bpy.context.scene.frame_current

        # Go to start of range
        bpy.context.scene.frame_set(physics_props.motion_path_frame_start)

        for f in range(physics_props.frame_start, physics_props.motion_path_frame_end + 1):
            # Add motion path point
            motion_path_points.add()

            # Set Frame
            bpy.context.scene.frame_set(f)

            # Get center of mass
            group_com = get_com(sel_mog.mass_object_collection.all_objects)

            # Set created point as center of mass
            motion_path_points[-1].point_location = group_com

        # Return to original frame
        bpy.context.scene.frame_set(original_frame)

        return {'FINISHED'}


class ClearBPMotionPath(bpy.types.Operator):
    """Clears Calculated Center of Mass Motion Path."""
    bl_idname = "balance_point.clear_motion_path"
    bl_label = "Clear Motion Path"

    @classmethod
    def poll(cls, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]

        return len(sel_mog.motion_path_points) > 0

    def execute(self, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        mois = sel_mog.motion_path_points

        mois.clear()
        bpy.context.region.tag_redraw()
        return {'FINISHED'}
