import bpy
from .utils import get_total_mass, get_moment_of_inertia, get_com
from mathutils import Vector


class BalancePointPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Balance Point"


class BP_UL_List(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_property, index):
        row = layout.row(align=True)
        row.prop(item, "visible", text="", emboss=True)
        row.prop(item, "name", text="", emboss=False)
        weight_col = row.column()
        weight_col.scale_x = 0.6
        total_mass = 0
        if item.mass_object_collection is not None:
            total_mass = get_total_mass(
                item.mass_object_collection.all_objects)
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
        com_props = scene.com_properties
        phys_props = scene.bp_physics_properties
        mass_object_groups = scene.bp_mass_object_groups
        selected_index = scene.bp_group_index
        selected_mog = mass_object_groups[selected_index] if selected_index < len(
            mass_object_groups) else None

        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Mass Object Groups")
        row = layout.row()
        row.template_list("BP_UL_List", "my_custom_list", scene,
                          "bp_mass_object_groups", scene, "bp_group_index", rows=3)
        col = row.column(align=True)
        col.operator("balance_point.massgroup_add", icon='ADD', text="")
        col.operator("balance_point.massgroup_remove", icon='REMOVE', text="")
        col.separator()
        draw_icon = 'HIDE_OFF' if com_props.com_drawing_on else 'HIDE_ON'
        col.prop(com_props, "com_drawing_on", toggle=1,
                 icon=draw_icon, text="")

        if selected_mog is not None:
            box = layout.box()
            row = box.row()
            # MOG Settings
            row.alignment = 'CENTER'
            row.label(text=selected_mog.name + " Settings")
            # Collection
            main_box = box.box()
            row = main_box.row()
            row.scale_y = 1.5
            row.prop(selected_mog, "mass_object_collection",
                     text="Mass Collection")

            # MOG Info
            row = main_box.row()
            row.prop(selected_mog, "com_location")
            row = main_box.row()
            row.prop(selected_mog, "pinned_rig")

            # Physics
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text="Physics Settings")

            if selected_mog.pinned_rig is not None:
                phys_box = box.box()
                row = phys_box.row()
                row.alignment = 'CENTER'
                row.scale_y = 1.2
                row.prop(selected_mog, "is_rig_pinned")

                # Reference Points
                point_box = phys_box.box()
                ref_header_row = point_box.row()
                ref_header_row.alignment = 'CENTER'
                col1 = ref_header_row.column()
                preview_on = selected_mog.show_reference_point
                col1.prop(selected_mog, "show_reference_point", text="",
                          icon='HIDE_OFF' if preview_on else 'HIDE_ON')
                col2 = ref_header_row.column()
                t_row = col2.row()
                t_row.alignment = 'CENTER'
                t_row.label(text="Reference Points")

                # Left Starting Point Column
                points_split = point_box.split()
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
                col.operator("balance_point.referencepointcom_set",
                             icon='DOT', text="Center of Mass")

                # Axis
                axis_box = phys_box.box()

                # Axis Header
                axis_header = axis_box.row()
                axis_header.alignment = 'CENTER'
                preview_on = selected_mog.show_axis
                axis_header.prop(selected_mog, "show_axis", text="",
                                 icon='HIDE_OFF' if preview_on else 'HIDE_ON')
                axis_header.label(text="Rotation Axis")

                row = axis_box.row()
                row.enabled = selected_mog.is_rig_pinned
                row.prop(selected_mog.pinned_rig,
                         "rotation_axis_angle", text="")
                moment_of_inertia = 0.0
                center_of_mass = get_com(
                    selected_mog.mass_object_collection.all_objects)
                current_axis = Vector(
                    (selected_mog.pinned_rig.rotation_axis_angle[1], selected_mog.pinned_rig.rotation_axis_angle[2], selected_mog.pinned_rig.rotation_axis_angle[3]))
                moment_of_inertia = get_moment_of_inertia(
                    selected_mog.mass_object_collection.all_objects, center_of_mass, current_axis)
                row = axis_box.row()
                row.alignment = 'CENTER'
                row.label(text="Moment of Inertia: {} kg·m2".format(
                    round(moment_of_inertia, 3)))
                row = axis_box.row()
                row.operator("balance_point.align_axis_cursor", icon='CURSOR')
                row.operator("balance_point.align_axis", icon='DOT')

                # Ballistics Ruler
                ballistics_box = phys_box.box()
                ballistics_box.use_property_split = True
                ballistics_box.use_property_decorate = False
                row = ballistics_box.row()
                row.alignment = 'CENTER'
                preview_on = phys_props.is_ballistics_preview
                row.prop(phys_props, "is_ballistics_preview", text="",
                         icon='HIDE_OFF' if preview_on else 'HIDE_ON')
                row.label(text="Ballistics")
                col = ballistics_box.column(align=True)
                col.prop(phys_props, "gravity")
                col.prop(phys_props, "time_of_flight")
                row = ballistics_box.row()
                col = row.column()
                col.prop(phys_props, "initial_angular_velocity")
                row = col.row()
                col_l = row.column()
                col_l.operator(
                    "balance_point.calculate_angle_preview", icon="CURVE_PATH")
                col_r = row.column()
                col_r.scale_x = 0.6
                col_r.operator("balance_point.clear_angle_preview",
                               text="Clear", icon="PANEL_CLOSE")

                # Baking
                bake_box = phys_box.box()
                bake_box.use_property_split = True
                bake_box.use_property_decorate = False
                row = bake_box.row()
                row.alignment = 'CENTER'
                row.label(text='Baking')
                col = bake_box.column(align=True)
                col.prop(phys_props, "frame_start")
                col.prop(phys_props, "frame_end")
                col.prop(phys_props, "frame_rate")
                row = bake_box.row()
                row.operator("balance_point.bake_physics")

            else:
                row = box.row()
                row.alignment = 'CENTER'
                row.label(text="Add a Pinned Rig.")


class BP_PT_MassPropertyEditor(BalancePointPanel, bpy.types.Panel):
    """Mass properties panel"""
    bl_label = "Mass Property Editing"
    bl_idname = "BP_PT_MassPropertyEditor"

    def draw(self, context):
        layout = self.layout
        sel_obj = context.selected_objects
        com_props = context.scene.com_properties

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