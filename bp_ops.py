import bpy
from math import radians
from .utils import (
    is_valid_triangle,
    get_triangle_normal,
    get_inertia_tensor,
    projectile_position_linear,
    get_com
)
from mathutils import Vector, Quaternion


class BP_AddMassCollection(bpy.types.Operator):
    """Add new Mass Collection to Current Mass Object Group."""
    bl_idname = "balance_point.masscollection_add"
    bl_label = "Add New Mass Collection"

    def execute(self, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        sel_mog.mass_collections.add()
        return {'FINISHED'}


class BP_RemoveMassCollection(bpy.types.Operator):
    """Remove last Mass Collection to Current Mass Object Group."""
    bl_idname = "balance_point.masscollection_remove"
    bl_label = "Remove Last Mass Collection"

    @classmethod
    def poll(cls, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        return len(sel_mog.mass_collections) > 0

    def execute(self, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        sel_mog.mass_collections.remove(len(sel_mog.mass_collections) - 1)
        return {'FINISHED'}


class AddMassObjectGroup(bpy.types.Operator):
    """Adds a new Mass Object Group."""
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
    """Removes a new Mass Object Group."""
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

    @classmethod
    def poll(cls, context):
        selected_index = context.scene.bp_group_index
        mass_object_groups = context.scene.bp_mass_object_groups
        
        return selected_index < len(mass_object_groups)

    def execute(self, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        cursor_loc = context.scene.cursor.location
        cursor_coords = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

        sel_mog.reference_point = cursor_coords

        bpy.context.region.tag_redraw()
        return {'FINISHED'}


class SetReferencePointToCOM(bpy.types.Operator):
    """Sets the coordinate of ballistics reference point to the center of mass."""
    bl_idname = "balance_point.referencepointcom_set"
    bl_label = "Set Reference Point To Center of Mass"

    @classmethod
    def poll(cls, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        return any(group.mass_object_collection is not None for group in sel_mog.mass_collections)

    def execute(self, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        sel_mog.reference_point = get_com(sel_mog)

        bpy.context.region.tag_redraw()
        return {'FINISHED'}


class SetStartingPoint(bpy.types.Operator):
    """Sets the coordinate of the ballistics starting point to the 3D cursor."""
    bl_idname = "balance_point.startingpoint_set"
    bl_label = "Set Starting Point From 3D Cursor"

    @classmethod
    def poll(cls, context):
        selected_index = context.scene.bp_group_index
        mass_object_groups = context.scene.bp_mass_object_groups
        
        return selected_index < len(mass_object_groups)

    def execute(self, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        cursor_loc = context.scene.cursor.location
        cursor_coords = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

        sel_mog.ballistics_starting_point = cursor_coords

        bpy.context.region.tag_redraw()
        return {'FINISHED'}


class SetStartingPointToCOM(bpy.types.Operator):
    """Sets the coordinate of the ballistics starting point to the center of mass."""
    bl_idname = "balance_point.startingpointcom_set"
    bl_label = "Set Starting Point From Center of Mass"

    @classmethod
    def poll(cls, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        return any(group.mass_object_collection is not None for group in sel_mog.mass_collections)

    def execute(self, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        sel_mog.ballistics_starting_point = get_com(sel_mog)

        bpy.context.region.tag_redraw()
        return {'FINISHED'}


class AlignAxisByPoints(bpy.types.Operator):
    """Aligns rotation axis to face the reference point."""
    bl_idname = "balance_point.align_axis"
    bl_label = "Align Axis to Reference Point"

    @classmethod
    def poll(cls, context):
        selected_index = context.scene.bp_group_index
        mass_object_groups = context.scene.bp_mass_object_groups
        
        return selected_index < len(mass_object_groups)

    def execute(self, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        rig_com = get_com(sel_mog)

        p1 = sel_mog.reference_point
        p2 = [sel_mog.reference_point[0], sel_mog.reference_point[1],
              sel_mog.reference_point[2] + 1]
        p3 = [rig_com[0], rig_com[1], rig_com[2]]
        if is_valid_triangle(p1, p2, p3):
            norm = get_triangle_normal(p3, p2, p1)
            sel_mog.initial_axis.x = norm[0]
            sel_mog.initial_axis.y = norm[1]
            sel_mog.initial_axis.z = norm[2]
            bpy.context.region.tag_redraw()
        else:
            print("Not a valid triangle.")
        return {'FINISHED'}


class AlignAxisByCursor(bpy.types.Operator):
    """Aligns rotation axis to face the 3D Cursor."""
    bl_idname = "balance_point.align_axis_cursor"
    bl_label = "Align Axis to 3D Cursor"

    @classmethod
    def poll(cls, context):
        selected_index = context.scene.bp_group_index
        mass_object_groups = context.scene.bp_mass_object_groups
        
        return selected_index < len(mass_object_groups)

    def execute(self, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        rig_com = get_com(sel_mog)
        cursor = context.scene.cursor.location

        p1 = cursor
        p2 = [cursor[0], cursor[1], cursor[2] + 1]
        p3 = [rig_com[0], rig_com[1], rig_com[2]]
        if is_valid_triangle(p1, p2, p3):
            norm = get_triangle_normal(p3, p2, p1)
            sel_mog.initial_axis.x = norm[0]
            sel_mog.initial_axis.y = norm[1]
            sel_mog.initial_axis.z = norm[2]
            bpy.context.region.tag_redraw()
        else:
            print("Not a valid triangle.")
        return {'FINISHED'}


class AlignAxisByCursorRef(bpy.types.Operator):
    """Aligns rotation axis according to 3D Cursor and Reference Point."""
    bl_idname = "balance_point.align_axis_cursor_ref"
    bl_label = "Align Axis to 3D Cursor and Reference Point"

    @classmethod
    def poll(cls, context):
        selected_index = context.scene.bp_group_index
        mass_object_groups = context.scene.bp_mass_object_groups
        
        return selected_index < len(mass_object_groups)

    def execute(self, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        rig_com = get_com(sel_mog)
        cursor = context.scene.cursor.location

        p1 = cursor
        p2 = sel_mog.reference_point
        p3 = [rig_com[0], rig_com[1], rig_com[2]]
        if is_valid_triangle(p1, p2, p3):
            norm = get_triangle_normal(p3, p2, p1)
            sel_mog.initial_axis.x = norm[0]
            sel_mog.initial_axis.y = norm[1]
            sel_mog.initial_axis.z = norm[2]
            bpy.context.region.tag_redraw()
        else:
            print("Not a valid triangle.")
        return {'FINISHED'}


class BakeBPPhysics(bpy.types.Operator):
    """Bakes the rotation and ballistics curve for the given range."""
    bl_idname = "balance_point.bake_physics"
    bl_label = "Bake Physics"

    @classmethod
    def poll(cls, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        if sel_mog.frame_end <= sel_mog.frame_start:
            return False

        if sel_mog.root_bone not in sel_mog.pinned_rig.pose.bones:
            return False

        return True

    def execute(self, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]
        root_bone = sel_mog.pinned_rig.pose.bones[sel_mog.root_bone]

        # For returning to original frame after operation
        original_frame = bpy.context.scene.frame_current

        bpy.context.scene.frame_set(sel_mog.frame_start)
        context.view_layer.update()

        com_start = get_com(sel_mog)
        starting_inertia = get_inertia_tensor(sel_mog, com_start)

        initial_angular_velocity = Vector(sel_mog.initial_axis).normalized() * radians(sel_mog.initial_angular_velocity)
        momentum_vector = starting_inertia @ initial_angular_velocity
        accumulated_rotation = root_bone.matrix.to_quaternion()

        # Cache initial mass data
        mass_obj_data = []
        for mc in sel_mog.mass_collections:
            if mc.mass_object_collection:
                for obj in mc.mass_object_collection.objects:
                    density = obj.get("density", 1.0)
                    volume = obj.get("volume", 1.0)
                    mass = density * volume * mc.influence
                    mass_obj_data.append((obj, mass))

        prev_local_rel_pos = {}
        R_inv = accumulated_rotation.inverted().to_matrix()
        for obj, mass in mass_obj_data:
            r_world = obj.matrix_world.translation - com_start
            prev_local_rel_pos[obj] = R_inv @ r_world


        p0 = sel_mog.ballistics_starting_point
        p1 = sel_mog.reference_point

        fps = float(sel_mog.frame_rate)
        dt_frame = 1.0 / fps
        substeps = sel_mog.substeps
        dt_sub = dt_frame / substeps

        for f in range(sel_mog.frame_start, sel_mog.frame_end + 1):
            bpy.context.scene.frame_set(f)

            if sel_mog.enable_ballistics_rotation:
                # Internal Angular Momentum
                L_int_local = Vector((0.0, 0.0, 0.0))
                R_inv_curr = accumulated_rotation.inverted().to_matrix()

                if f > sel_mog.frame_start:
                    for obj, mass in mass_obj_data:
                        r_world = obj.matrix_world.translation - get_com(sel_mog)
                        r_local = R_inv_curr @ r_world
                        
                        v_local = (r_local - prev_local_rel_pos[obj]) / dt_frame
                        
                        L_int_local += mass * r_local.cross(v_local)
                        
                        prev_local_rel_pos[obj] = r_local

                # Rotation
                current_inertia_world = get_inertia_tensor(sel_mog, get_com(sel_mog))

                R_start = accumulated_rotation.to_matrix()
                I_body = R_start.transposed() @ current_inertia_world @ R_start

                L_int_world = R_start @ L_int_local

                # Rotation substeps
                for _ in range(substeps):
                    R_curr = accumulated_rotation.to_matrix()
                    I_curr_world = R_curr @ I_body @ R_curr.transposed()

                    # Subtract internal momentum from the total conserved momentum
                    effective_momentum = momentum_vector - L_int_world
                    current_ang_vel = I_curr_world.inverted_safe() @ effective_momentum

                    rotation_angle = current_ang_vel.length * dt_sub
                    
                    if rotation_angle > 1e-6 and f > sel_mog.frame_start:
                        rotation_axis = current_ang_vel.normalized()
                        rot_step = Quaternion(rotation_axis, rotation_angle)
                        accumulated_rotation = rot_step @ accumulated_rotation
                        accumulated_rotation.normalize()

                root_bone.rotation_quaternion = accumulated_rotation
                root_bone.keyframe_insert(data_path="rotation_quaternion", keytype='GENERATED')
                context.view_layer.update()

            # Ballistics
            start_pos = (p0[0], p0[1], p0[2])
            ref_pos = (p1[0], p1[1], p1[2])
            gravity = sel_mog.gravity
            time_of_flight = float(sel_mog.time_of_flight)

            elapsed_time = float(f - sel_mog.frame_start) / sel_mog.frame_rate

            point_position = projectile_position_linear(
                start_pos, ref_pos, gravity, time_of_flight, elapsed_time, sel_mog.damp_vector)

            difference = get_com(sel_mog) - point_position
            if difference.length > 0.00001:
                world_space_diff = sel_mog.pinned_rig.matrix_world.inverted().to_3x3() @ Vector((difference.x, difference.y, difference.z))
                sel_mog.pinned_rig.pose.bones[sel_mog.root_bone].location -= world_space_diff

            root_bone.keyframe_insert(data_path="location", keytype='GENERATED')

        # Return to original state
        bpy.context.scene.frame_set(original_frame)
        return {'FINISHED'}


class BakeBPRootMotion(bpy.types.Operator):
    """Bakes Root Motion for the given frame range."""
    bl_idname = "balance_point.bake_root_motion"
    bl_label = "Bake Root Motion"

    @classmethod
    def poll(cls, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        if sel_mog.pinned_rig is None:
            return False

        if sel_mog.root_bone == "":
            return False

        if len(sel_mog.root_control_bones) < 1:
            return False

        return True

    def execute(self, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]
        pinned_rig = sel_mog.pinned_rig
        root_bone = pinned_rig.pose.bones[sel_mog.root_bone]
        root_limit = sel_mog.root_limit_xyz
        root_fixed = sel_mog.root_bake_relative_xyz

        animation_cache = []

        for f in range(sel_mog.root_motion_frame_start, sel_mog.root_motion_frame_end + 1):
            context.scene.frame_set(f)

            new_root_location = Vector((root_limit[0], root_limit[1], root_limit[2]))
            current_com = get_com(sel_mog)
            if sel_mog.root_bake_relative:
                new_root_location.x = current_com[0] + root_fixed[0]
                new_root_location.y = current_com[1] + root_fixed[1]
                new_root_location.z = current_com[2] + root_fixed[2]
            else:
                if sel_mog.root_track_xyz[0]:
                    new_root_location.x = current_com[0]
                if sel_mog.root_track_xyz[1]:
                    new_root_location.y = current_com[1]
                if sel_mog.root_track_xyz[2]:
                    new_root_location.z = current_com[2]

            control_bone_matrices = {cb.control_bone: pinned_rig.matrix_world @ pinned_rig.pose.bones[cb.control_bone].matrix.copy() for cb in sel_mog.root_control_bones}

            animation_cache.append(
                {
                    "frame": f,
                    "root_com": pinned_rig.matrix_world.inverted() @ new_root_location,
                    "control_bone_matrices": control_bone_matrices
                }
            )

        for data in animation_cache:
            f = data["frame"]
            context.scene.frame_set(f)

            root_bone.matrix.translation = data["root_com"]
            if sel_mog.root_bake_clear_rotation:
                root_bone.rotation_quaternion = Quaternion((1.0, 0.0, 0.0, 0.0))

            context.view_layer.update()

            for control_bone_name, saved_matrix in data["control_bone_matrices"].items():
                cb = pinned_rig.pose.bones.get(control_bone_name)

                if cb:
                    cb.matrix = pinned_rig.matrix_world.inverted() @ saved_matrix

                    cb.keyframe_insert(data_path="location", index=-1, keytype='GENERATED')
                    cb.keyframe_insert(data_path="scale", index=-1, keytype='GENERATED')

                    if cb.rotation_mode == 'QUATERNION':
                        cb.keyframe_insert(data_path="rotation_quaternion", index=-1, keytype='GENERATED')
                    elif cb.rotation_mode == 'AXIS_ANGLE':
                        cb.keyframe_insert(data_path="rotation_axis_angle", index=-1, keytype='GENERATED')
                    else:
                        cb.keyframe_insert(data_path="rotation_euler", index=-1, keytype='GENERATED')

            if sel_mog.root_bake_clear_rotation:
                root_bone.keyframe_insert(data_path="rotation_quaternion", index=-1, keytype='GENERATED')
            root_bone.keyframe_insert(data_path="location", index=-1, keytype='GENERATED')

        return {'FINISHED'}


class BP_RootSetRelativeZ(bpy.types.Operator):
    """Set Relative Root Motion Z Offset to current distance from Center of Mass to Root Bone."""
    bl_idname = "balance_point.root_set_z_relative"
    bl_label = "Set Current COM Height to Z Distance"

    @classmethod
    def poll(cls, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        if all(group.mass_object_collection is None for group in sel_mog.mass_collections):
            return False

        if sel_mog.pinned_rig is None:
            return False

        if sel_mog.root_bone == "":
            return False

        return True

    def execute(self, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]
        root_bone = sel_mog.pinned_rig.pose.bones[sel_mog.root_bone]
        current_com_height = get_com(sel_mog).z

        root_world_matrix = sel_mog.pinned_rig.matrix_world @ root_bone.matrix

        sel_mog.root_bake_relative_xyz.z = root_world_matrix.translation.z - current_com_height

        return {'FINISHED'}


class BP_AddControlBones(bpy.types.Operator):
    """Adds selected control bones to counter-animate for root motion baking."""
    bl_idname = "balance_point.add_control_bones"
    bl_label = "Add Selected Control Bones"

    @classmethod
    def poll(cls, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]
        selected_bones = context.selected_pose_bones_from_active_object

        if sel_mog.pinned_rig is None:
            return False

        if sel_mog.root_bone == "":
            return False

        if selected_bones is None:
            return False

        return True

    def execute(self, context):
        sel_mog = context.scene.bp_mass_object_groups[context.scene.bp_group_index]
        selected_bones = context.selected_pose_bones_from_active_object

        if len(selected_bones) > 0:
            for bone in selected_bones:
                if not any(cb.control_bone == bone.name for cb in sel_mog.root_control_bones):
                    new_bone_prop = sel_mog.root_control_bones.add()
                    new_bone_prop.control_bone = bone.name

        return {'FINISHED'}


class BP_DeleteControlBone(bpy.types.Operator):
    """Clears set control bone used for root motion baking."""
    bl_idname = "balance_point.delete_control_bone"
    bl_label = "Unset Control Bone"

    index: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        return len(sel_mog.root_control_bones) > 0

    def execute(self, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]
        control_bones = sel_mog.root_control_bones

        if 0 <= self.index < len(control_bones):
            control_bones.remove(self.index)

        return {'FINISHED'}


class CalculateBPMotionPath(bpy.types.Operator):
    """Calculate the motion path of the mass object group's center of mass for the given range."""
    bl_idname = "balance_point.calculate_com_motion_path"
    bl_label = "Calculate Center of Mass Motion Path"

    @classmethod
    def poll(cls, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]

        if sel_mog.motion_path_frame_end <= sel_mog.motion_path_frame_start:
            return False

        return True

    def execute(self, context):
        selected_index = context.scene.bp_group_index
        sel_mog = context.scene.bp_mass_object_groups[selected_index]
        motion_path_points = sel_mog.motion_path_points

        # Clear points
        motion_path_points.clear()

        # For returning to original frame after operation
        original_frame = bpy.context.scene.frame_current

        # Go to start of range
        bpy.context.scene.frame_set(sel_mog.motion_path_frame_start)

        for f in range(sel_mog.frame_start, sel_mog.motion_path_frame_end + 1):
            # Add motion path point
            motion_path_points.add()

            # Set Frame
            bpy.context.scene.frame_set(f)

            # Get center of mass
            group_com = get_com(sel_mog)

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
