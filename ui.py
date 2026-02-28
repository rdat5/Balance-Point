import bpy
from .utils import (
    get_inertia_tensor,
    get_com,
    get_total_mass,
    get_total_mog_mass,
)


class BalancePointPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Balance Point"


class BP_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon,
                  active_data, active_property, index):
        row = layout.row(align=True)
        row.prop(item, "visible", text="", emboss=True)
        row.prop(item, "name", text="", emboss=False)
        weight_col = row.column()
        weight_col.scale_x = 0.6
        total_mass = 0
        if any(mass_collection is not None for mass_collection in item.mass_collections):
            total_mass = get_total_mog_mass(item)
        weight_col.label(text="{} kg".format(round(total_mass, 2)))
        color_col = row.column()
        color_col.scale_x = 0.35
        color_col.prop(item, "color", text="", emboss=True)


class BP_PT_MainMenu(BalancePointPanel, bpy.types.Panel):
    bl_idname = "BP_PT_MainMenu"
    bl_label = "Balance Point"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        com_props = scene.bp_com_properties
        mass_object_groups = scene.bp_mass_object_groups
        selected_index = scene.bp_group_index
        selected_mog = mass_object_groups[selected_index] if selected_index < len(
            mass_object_groups) else None

        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Mass Object Groups")
        row = layout.row()
        row.template_list("BP_UL_List", "balance_point_group_list", scene,
                          "bp_mass_object_groups", scene, "bp_group_index", rows=3)
        col = row.column(align=True)
        col.operator("balance_point.massgroup_add", icon='ADD', text="")
        col.operator("balance_point.massgroup_remove", icon='REMOVE', text="")
        col.separator()
        draw_icon = 'HIDE_OFF' if com_props.com_drawing_on else 'HIDE_ON'
        col.prop(com_props, "com_drawing_on", toggle=1,
                 icon=draw_icon, text="")

        # MOG Settings
        if selected_mog is not None:
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(text=selected_mog.name + " Settings")
            box = layout.box()
            if len(selected_mog.mass_collections) > 0:
                row = box.row(align=True)
                row.alignment = 'CENTER'
                row.label(text="Mass Collections")
                row.operator("balance_point.masscollection_add",
                             icon='ADD', text="Add New")
                row.operator("balance_point.masscollection_remove",
                             text="", icon='REMOVE')
            for mc in selected_mog.mass_collections:
                row = box.row(align=True)
                col = row.column()
                col.scale_x = 1.5
                col.prop(mc, "mass_object_collection", text="")
                col = row.column()
                row.prop(mc, "influence", text="")
            if len(selected_mog.mass_collections) < 1:
                row = box.row()
                row.scale_y = 2.0 if len(
                    selected_mog.mass_collections) == 0 else 1.0
                row.operator("balance_point.masscollection_add", icon='ADD')

            # MOG Info
            row = layout.row()
            row.prop(selected_mog, "com_location")
            row = layout.row()
            row.prop(selected_mog, "pinned_rig")
            if selected_mog.pinned_rig is not None and selected_mog.pinned_rig.type == 'ARMATURE':
                row = layout.row()
                row.prop_search(
                    selected_mog,
                    "root_bone",
                    selected_mog.pinned_rig.data,
                    "bones",
                    text="Root Bone")
                if selected_mog.root_bone != '':
                    if selected_mog.pinned_rig.pose.bones[selected_mog.root_bone].rotation_mode != 'QUATERNION':
                        row = layout.row()
                        row.label(
                            text="Set root bone rotation to Quaternion to use Angular Momentum Features.")
                        row = layout.row()
                        row.prop(
                            selected_mog.pinned_rig.pose.bones[selected_mog.root_bone], "rotation_mode")
            row = layout.row()
            row.prop(selected_mog, "com_object_enabled")
            row = layout.row()
            row.prop(selected_mog, "com_object")

            # COM Floor
            row = layout.row()
            row.prop(selected_mog, "com_floor_level")


class BP_PT_DrawSettings(BalancePointPanel, bpy.types.Panel):
    bl_parent_id = "BP_PT_MainMenu"
    bl_label = "Draw Settings"

    def draw(self, context):
        layout = self.layout
        com_props = context.scene.bp_com_properties

        layout.use_property_split = True
        layout.use_property_decorate = False
        col = layout.column(align=True)
        col.prop(com_props, "com_point_size")
        col.prop(com_props, "floor_com_size")
        col.prop(com_props, "reference_point_size")
        col.prop(com_props, "ballistics_point_size")
        col.prop(com_props, "motion_path_point_size")
        col.prop(com_props, "rotation_axis_line_size")
        col.prop(com_props, "opacity")


class BP_PT_PhysicsTools(BalancePointPanel, bpy.types.Panel):
    bl_idname = "BP_PT_PhysicsTools"
    bl_label = "Physics Tools"

    def draw(self, context):
        pass


class BP_PT_ReferencePoints(BalancePointPanel, bpy.types.Panel):
    bl_parent_id = "BP_PT_PhysicsTools"
    bl_label = "Reference Points"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mass_object_groups = scene.bp_mass_object_groups
        selected_index = scene.bp_group_index
        selected_mog = mass_object_groups[selected_index] if selected_index < len(
            mass_object_groups) else None

        # Reference Points
        ref_header_row = layout.row()
        ref_header_row.alignment = 'CENTER'
        if selected_mog is not None:
            col1 = ref_header_row.column()
            preview_on = selected_mog.show_reference_point
            col1.prop(selected_mog, "show_reference_point", text="",
                      icon='HIDE_OFF' if preview_on else 'HIDE_ON')
            col2 = ref_header_row.column()
            t_row = col2.row()
            t_row.alignment = 'CENTER'
            t_row.label(text="Reference Points")

            # Left Starting Point Column
            points_split = layout.split()
            left_col = points_split.column()
            starting_box = left_col.box()
            start_header_row = starting_box.row(align=True)
            start_header_row.alignment = 'CENTER'

            left_col = start_header_row.column()
            start_head = left_col.row()
            start_head.alignment = 'CENTER'
            start_head.label(text="Start Point")
            right_col = start_header_row.column()
            col = right_col.row()
            col.scale_x = 0.35
            col.prop(selected_mog, "ballistics_starting_point_color", text="")

            row = starting_box.row()
            row.prop(selected_mog, "ballistics_starting_point", text="")
            row = starting_box.row()
            row.alignment = 'CENTER'
            row.label(text="Set Starting Point To")
            row = starting_box.row()
            col = row.column(align=True)
            col.operator("balance_point.startingpoint_set",
                         icon='CURSOR', text="3D Cursor")
            if any(mass_collection is not None for mass_collection in selected_mog.mass_collections):
                col.operator("balance_point.startingpointcom_set",
                             icon='DOT', text="Center of Mass")

            # Right Reference Point Column
            right_col = points_split.column()
            ref_box = right_col.box()
            ref_header = ref_box.row(align=True)
            ref_header.alignment = 'CENTER'
            left_col = ref_header.column()
            row = left_col.row()
            row.alignment = 'CENTER'
            ref_header.label(text="Reference Point")
            right_col = ref_header.column()
            col = right_col.row()
            col.scale_x = 0.35
            col.prop(selected_mog, "reference_color", text="")

            row = ref_box.row()
            row.prop(selected_mog, "reference_point", text="")
            row = ref_box.row()
            row.alignment = 'CENTER'
            row.label(text="Set Reference Point To")
            row = ref_box.row()
            col = row.column(align=True)
            col.operator("balance_point.referencepoint_set",
                         icon='CURSOR', text="3D Cursor")
            if any(mass_collection is not None for mass_collection in selected_mog.mass_collections):
                col.operator("balance_point.referencepointcom_set",
                             icon='DOT', text="Center of Mass")
        else:
            ref_header_row.label(
                text="Add and select a mass object group to use the reference point features.")


class BP_PT_RotationAxis(BalancePointPanel, bpy.types.Panel):
    bl_parent_id = "BP_PT_PhysicsTools"
    bl_label = "Rotation Axis"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mass_object_groups = scene.bp_mass_object_groups
        selected_index = scene.bp_group_index
        selected_mog = mass_object_groups[selected_index] if selected_index < len(
            mass_object_groups) else None

        # Axis
        if selected_mog is not None and selected_mog.pinned_rig is not None and any(mass_collection is not None for mass_collection in selected_mog.mass_collections) and selected_mog.root_bone != '':
            # Axis Header
            axis_header = layout.row()
            axis_header.alignment = 'CENTER'
            preview_on = selected_mog.show_axis
            axis_header.prop(selected_mog, "show_axis", text="",
                             icon='HIDE_OFF' if preview_on else 'HIDE_ON')
            axis_header.label(text="Rotation Axis")

            row = layout.row()
            row.prop(selected_mog, "initial_axis", text="")
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(
                text=f"Inertia Tensor: {format_matrix(get_inertia_tensor(selected_mog, get_com(selected_mog)))}")
            row = layout.row()
            row.operator("balance_point.align_axis_cursor", icon='CURSOR')
            row.operator("balance_point.align_axis", icon='DOT')
            row = layout.row()
            row.operator(
                "balance_point.align_axis_cursor_ref",
                icon='OUTLINER_DATA_MESH')
        else:
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(
                text="Add an Armature and Root Bone to use the rotation axis features.")


class BP_PT_BallisticsRuler(BalancePointPanel, bpy.types.Panel):
    bl_parent_id = "BP_PT_PhysicsTools"
    bl_label = "Ballistics Ruler"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mass_object_groups = scene.bp_mass_object_groups
        selected_index = scene.bp_group_index
        selected_mog = mass_object_groups[selected_index] if selected_index < len(
            mass_object_groups) else None

        layout.use_property_split = True
        layout.use_property_decorate = False
        row = layout.row()
        row.alignment = 'CENTER'
        if selected_mog is not None:
            preview_on = selected_mog.is_ballistics_preview
            row.prop(selected_mog, "is_ballistics_preview", text="",
                     icon='HIDE_OFF' if preview_on else 'HIDE_ON')
            row.label(text="Ballistics")
            col = layout.column(align=True)
            col.prop(selected_mog, "frame_start")
            col.prop(selected_mog, "frame_end")
            col.prop(selected_mog, "frame_rate")
            col.separator()
            col.prop(selected_mog, "gravity")
            col.prop(selected_mog, "time_of_flight")
            col.separator()
            col.prop(selected_mog, "damp_vector")
            vt = get_terminal_velocity(selected_mog.gravity, selected_mog.damp_vector[2])
            col.label(text=f"Terminal Velocity: {vt:.3f} m/s" if selected_mog.damp_vector[2] > 0 else "Terminal Velocity: None")
        else:
            row.label(
                text="Add and select a mass object group to use the ballistics features.")


class BP_PT_Baking(BalancePointPanel, bpy.types.Panel):
    bl_parent_id = "BP_PT_PhysicsTools"
    bl_label = "Baking"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mass_object_groups = scene.bp_mass_object_groups
        selected_index = scene.bp_group_index
        selected_mog = mass_object_groups[selected_index] if selected_index < len(
            mass_object_groups) else None

        # Baking
        if selected_mog is not None:
            layout.use_property_split = True
            layout.use_property_decorate = False
            col = layout.column(align=True)
            col.prop(selected_mog, "frame_start")
            col.prop(selected_mog, "frame_end")
            col.prop(selected_mog, "frame_rate")
            col.separator()
            col.prop(selected_mog, "enable_ballistics_rotation")
            if selected_mog.enable_ballistics_rotation:
                col.prop(selected_mog, "initial_angular_velocity")
            col.separator()
            col.prop(selected_mog, "substeps")

        if selected_mog is not None and selected_mog.pinned_rig is not None and selected_mog.root_bone != '':
            row = layout.row()
            row.scale_y = 1.5
            row.operator("balance_point.bake_physics")


class BP_PT_Motion_Path(BalancePointPanel, bpy.types.Panel):
    bl_parent_id = "BP_PT_MainMenu"
    bl_label = "Center of Mass Motion Path"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mass_object_groups = scene.bp_mass_object_groups
        selected_index = scene.bp_group_index
        selected_mog = mass_object_groups[selected_index] if selected_index < len(
            mass_object_groups) else None

        if selected_mog is not None and any(mass_collection is not None for mass_collection in selected_mog.mass_collections):
            layout.use_property_split = True
            layout.use_property_decorate = False
            col = layout.column(align=True)
            col.prop(selected_mog, "motion_path_frame_start")
            col.prop(selected_mog, "motion_path_frame_end", text="End")
            row = layout.row()
            col_l = row.column()
            col_l.operator(
                "balance_point.calculate_com_motion_path", icon="CURVE_PATH")
            col_r = row.column()
            col_r.scale_x = 0.6
            col_r.operator("balance_point.clear_motion_path",
                           text="Clear", icon="PANEL_CLOSE")
        else:
            row = layout.row()
            row.alignment = 'CENTER'
            row.label(
                text="Add a Mass Object Collection to use the motion path features.")


class BP_PT_Root_Motion(BalancePointPanel, bpy.types.Panel):
    bl_parent_id = "BP_PT_MainMenu"
    bl_label = "Root Motion Baking"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mass_object_groups = scene.bp_mass_object_groups
        selected_index = scene.bp_group_index
        selected_mog = mass_object_groups[selected_index] if selected_index < len(
            mass_object_groups) else None

        if selected_mog is not None and any(mass_collection is not None for mass_collection in selected_mog.mass_collections):
            col = layout.column(align=True)
            col.use_property_split = True
            col.use_property_decorate = False
            col.prop(selected_mog, "root_motion_frame_start")
            col.prop(selected_mog, "root_motion_frame_end", text="End")
            box = layout.box()
            box.enabled = not selected_mog.root_bake_relative
            row = box.row()
            row.prop(selected_mog, "root_track_xyz", text="Track COM")
            row = box.row()
            row.prop(selected_mog, "root_limit_xyz", text="Limit Location")
            row = layout.row()
            row.prop(selected_mog, "root_bake_relative")
            box = layout.box()
            box.enabled = selected_mog.root_bake_relative
            row = box.row()
            row.prop(selected_mog, "root_bake_relative_xyz", text="")
            row = box.row()
            row.operator("balance_point.root_set_z_relative")
            # Motion Bones
            box = layout.box()
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text="Control Bones")
            if selected_mog.pinned_rig is not None:
                row = box.row()
                row.operator("balance_point.add_control_bones", icon="ADD")
                for i, mb in enumerate(selected_mog.root_control_bones):
                    row = box.row()
                    row.prop_search(
                        mb,
                        "control_bone",
                        selected_mog.pinned_rig.data,
                        "bones",
                        text="")
                    op = row.operator(
                        "balance_point.delete_control_bone", icon='X', text="")
                    op.index = i
                row = layout.row()
                row.prop(selected_mog, "root_bake_clear_rotation")
                row = layout.row()
                row.scale_y = 1.5
                row.operator("balance_point.bake_root_motion")
            else:
                row = box.row()
                row.label(text="Add a rig to use Root Motion Baking")


class BP_PT_MassPropertyEditor(BalancePointPanel, bpy.types.Panel):
    """Mass properties panel"""
    bl_label = "Mass Property Editing"
    bl_idname = "BP_PT_MassPropertyEditor"

    def draw(self, context):
        layout = self.layout
        com_props = context.scene.bp_com_properties

        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Mass Properties")
        row = layout.row()
        row.operator("balance_point.massprop_add", text="Add", icon='ADD')
        row.operator("balance_point.massprop_del",
                     text="Remove", icon='REMOVE')
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Density")
        row = layout.row(align=True)
        row.prop(com_props, "mass_density_set", text="Density")
        sub = row.row()
        sub.scale_x = 1.5
        sub.operator("balance_point.set_density",
                     icon='OUTLINER_OB_POINTCLOUD')
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Volume")
        row = layout.row()
        row.operator("balance_point.calculate_volume", icon='CUBE')
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Origin Setting")
        row = layout.row()
        row.operator("object.origin_set", text="Origin to Center of Mass (Volume)",
                     icon='DOT').type = 'ORIGIN_CENTER_OF_VOLUME'
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Set Active")
        row = layout.row()
        row.operator("balance_point.set_active_true", icon='RADIOBUT_ON')
        row.operator("balance_point.set_active_false", icon='RADIOBUT_OFF')
        row = layout.row()
        row.operator("balance_point.toggle_active", icon='ARROW_LEFTRIGHT')


class BP_PT_MassSelected(BalancePointPanel, bpy.types.Panel):
    bl_parent_id = "BP_PT_MassPropertyEditor"
    bl_label = "Selected Mass Objects"

    def draw(self, context):
        layout = self.layout
        sel_obj = context.selected_objects

        row = layout.row()
        row.alignment = 'RIGHT'
        row.label(text="Total Mass: {} kg".format(
            round(get_total_mass(sel_obj), 4)))

        for obj in sel_obj:
            if obj.get("volume") is not None:
                box = layout.box()

                row = box.row()
                obj_active = 'RADIOBUT_ON' if obj.get(
                    "active") else 'RADIOBUT_OFF'
                row.label(text="", icon=obj_active)
                row.label(text=obj.name)
                sub = row.row()
                sub.alignment = 'RIGHT'
                obj_mass = round(obj.get("density") *
                                 obj.get("volume") * obj.get("active"), 4)
                sub.label(text="Mass: {} kg".format(obj_mass))

                row = box.row()
                row.prop(obj, '["density"]')
                row.prop(obj, '["volume"]')


def format_matrix(matrix):
    vec1 = f"{round(matrix[0][0], 1), round(matrix[0][1], 1), round(matrix[0][2], 1)}"
    vec2 = f"{round(matrix[1][0], 1), round(matrix[1][1], 1), round(matrix[1][2], 1)}"
    vec3 = f"{round(matrix[2][0], 1), round(matrix[2][1], 1), round(matrix[2][2], 1)}"
    return f"{vec1} | {vec2} | {vec3}"


def get_terminal_velocity(gravity, drag):
    if drag < 1e-5:
        return float('inf')
    return gravity / drag
