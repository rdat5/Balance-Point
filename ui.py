import bpy
from .utils import get_total_mass, is_in_collection_group, get_moment_of_inertia, get_com
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
            total_mass = get_total_mass(item.mass_object_collection.all_objects)
        weight_col.label(text="{} kg".format(round(total_mass, 2)))
        color_col = row.column()
        color_col.scale_x = 0.35
        color_col.prop(item, "color", text="", emboss=True)


class NewBPMain(BalancePointPanel, bpy.types.Panel):
    bl_idname = "BP_PT_Main_new"
    bl_label = "Balance Point New"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        com_props = scene.com_properties
        phys_props = scene.bp_physics_properties
        mass_object_groups = scene.bp_mass_object_groups
        selected_index = scene.bp_group_index
        selected_mog = mass_object_groups[selected_index] if selected_index < len(mass_object_groups) else None

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
            # box.use_property_split = True
            row = box.row()
            # MOG Settings
            row.alignment = 'CENTER'
            row.label(text=selected_mog.name + " Settings")
            # Collection
            main_box = box.box()
            row = main_box.row()
            row.scale_y = 1.5
            row.prop(selected_mog, "mass_object_collection", text="Mass Collection")

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
                col1.prop(selected_mog, "show_reference_point", text="", icon='HIDE_OFF' if preview_on else 'HIDE_ON')
                col2 = ref_header_row.column()
                t_row = col2.row()
                t_row.alignment = 'CENTER'
                t_row.label(text='Reference Points')

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
                col.operator("balance_point.startingpoint_set", icon='CURSOR', text="3D Cursor")
                col.operator("balance_point.startingpointcom_set", icon='DOT', text="Center of Mass")

                # Right Reference Point Column
                right_col = points_split.column()
                ref_box = right_col.box()
                ref_header = ref_box.row(align=True)
                ref_header.alignment = 'CENTER'
                left_col = ref_header.column()
                row = left_col.row()
                row.alignment='CENTER'
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
                col.operator("balance_point.referencepoint_set", icon='CURSOR', text="3D Cursor")
                col.operator("balance_point.referencepointcom_set", icon='DOT', text="Center of Mass")


                # Axis
                axis_box = phys_box.box()

                # Axis Header
                axis_header = axis_box.row()
                axis_header.alignment = 'CENTER'
                preview_on = selected_mog.show_axis
                axis_header.prop(selected_mog, "show_axis", text="", icon='HIDE_OFF' if preview_on else 'HIDE_ON')
                axis_header.label(text="Rotation Axis")

                row = axis_box.row()
                row.enabled = selected_mog.is_rig_pinned
                row.prop(selected_mog.pinned_rig, "rotation_axis_angle", text="")
                moment_of_inertia = 0.0
                center_of_mass = get_com(selected_mog.mass_object_collection.all_objects)
                current_axis = Vector((selected_mog.pinned_rig.rotation_axis_angle[1], selected_mog.pinned_rig.rotation_axis_angle[2], selected_mog.pinned_rig.rotation_axis_angle[3]))
                moment_of_inertia = get_moment_of_inertia(selected_mog.mass_object_collection.all_objects, center_of_mass, current_axis)
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
                row.prop(phys_props, "is_ballistics_preview", text="", icon='HIDE_OFF' if preview_on else 'HIDE_ON')
                row.label(text='Ballistics')
                col = ballistics_box.column(align=True)
                col.prop(phys_props, "gravity")
                col.prop(phys_props, "time_of_flight")
                row = ballistics_box.row()
                col = row.column()
                col.prop(phys_props, "initial_angular_velocity")
                row = col.row()
                col_l = row.column()
                col_l.operator("balance_point.calculate_angle_preview", icon="CURVE_PATH")
                col_r = row.column()
                col_r.scale_x = 0.6
                col_r.operator("balance_point.clear_angle_preview", text="Clear", icon="PANEL_CLOSE")

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
            


class BalancePointMain(BalancePointPanel, bpy.types.Panel):
    bl_idname = "BP_PT_Main"
    bl_label = "Balance Point"

    def draw(self, context):
        layout = self.layout
        com_props = context.scene.com_properties
        row = layout.row()
        row.scale_y = 2.0

        track_icon = 'TRACKER' if com_props.com_tracking_on else 'DOT'
        track_text = 'Enabled' if com_props.com_tracking_on else 'Disabled'
        row.prop(com_props, "com_tracking_on", toggle=1,
                 icon=track_icon, text="CoM Tracking " + track_text)

        draw_icon = 'HIDE_OFF' if com_props.com_drawing_on else 'HIDE_ON'
        draw_text = 'Enabled' if com_props.com_drawing_on else 'Disabled'
        row.prop(com_props, "com_drawing_on", toggle=1,
                 icon=draw_icon, text="CoM Drawing " + draw_text)


class BP_PT_mass_object_groups(BalancePointPanel, bpy.types.Panel):
    bl_parent_id = "BP_PT_Main"
    bl_label = "Mass Object Groups"

    def draw(self, context):
        layout = self.layout
        bp_mass_groups = context.scene.bp_mass_object_groups

        for group in bp_mass_groups:
            box = layout.box()
            box.label(text=group.name)
            split = box.split(factor=0.1)
            # left
            col = split.column()
            col.scale_y = 5.0
            viz_icon = 'HIDE_OFF' if group.visible else 'HIDE_ON'
            col.prop(group, "visible", toggle=1, icon=viz_icon, text="")

            # right
            col = split.column()
            row = col.row()
            row.use_property_decorate = False
            row.prop(group, "mass_object_collection", text="Mass Objects")
            row = col.row()
            row.prop(group, "include_secondary_collection",
                     text="" if group.include_secondary_collection else "Include Secondary Mass Object Collection")
            if group.include_secondary_collection:
                row.prop(group, "secondary_mass_object_collection")
            row = col.row(align=True)
            row.scale_x = 0.3
            row.prop(group, "color", text="")
            row = col.row()
            row.prop(group, "com_floor_level")
            sub = row.row()
            sub.alignment = 'RIGHT'
            sub.prop(group, "line_to_floor")
            row = col.row()
            # row.prop(group, "use_com_object",
            #          text="" if group.use_com_object else "Use COM Object")
            # if group.use_com_object:
            #     row.prop(group, "com_object")
            #     row = col.row()
            #     row.prop(group, "is_rig_pinned",
            #              text="" if group.is_rig_pinned else "Pin Rig's COM to COM Object")
            #     if group.is_rig_pinned:
            #         row.prop(group, "pinned_rig")
            row = col.row()
            row.label(text="Total Mass")
            sub = row.row()
            sub.alignment = 'RIGHT'
            total_mass_text = '0'
            if group.mass_object_collection is not None:
                total_mass_text = round(get_total_mass(
                    group.mass_object_collection.all_objects), 4)
            sub.label(text="{} kg".format(total_mass_text))
            row = col.row()
            row.label(text="Center of Mass:")
            sub = row.row()
            sub.alignment = 'RIGHT'
            center_of_mass = (0.0, 0.0, 0.0)
            if group.mass_object_collection is not None:
                center_of_mass = get_com(group.mass_object_collection.all_objects)
            sub.label(text="({}, {}, {})".format(
                round(center_of_mass[0], 4), round(center_of_mass[1], 4), round(center_of_mass[2], 4)))

        row = layout.row()
        row.operator('balance_point.massgroup_remove', icon='REMOVE')
        row = layout.row()
        add_group_scale = 4.0 if len(bp_mass_groups) < 1 else 1.5
        row.scale_y = add_group_scale
        row.operator('balance_point.massgroup_add', icon='ADD')


class MassPropertiesPanel(BalancePointPanel, bpy.types.Panel):
    """Mass properties panel"""
    bl_label = "Mass Property Editing"
    bl_idname = "BP_PT_mass_editing_panel"

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
        row.operator("object.origin_set", text='Origin to Center of Mass (Volume)',
                     icon='DOT').type = 'ORIGIN_CENTER_OF_VOLUME'
        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Set Active")
        row = layout.row()
        row.operator("balance_point.set_active_true", icon='RADIOBUT_ON')
        row.operator("balance_point.set_active_false", icon='RADIOBUT_OFF')
        row = layout.row()
        row.operator("balance_point.toggle_active", icon='ARROW_LEFTRIGHT')


class BP_PT_mass_selected(BalancePointPanel, bpy.types.Panel):
    bl_parent_id = "BP_PT_mass_editing_panel"
    bl_label = "Selected Mass Objects"

    def draw(self, context):
        layout = self.layout
        sel_obj = context.selected_objects

        row = layout.row()
        row.alignment = 'RIGHT'
        row.label(text="Total Mass: {} kg".format(
            round(get_total_mass(sel_obj), 4)))

        for obj in sel_obj:
            if obj.get('volume') is not None:
                box = layout.box()

                row = box.row()
                obj_active = 'RADIOBUT_ON' if obj.get(
                    'active') else 'RADIOBUT_OFF'
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


class PhysicsPanel(BalancePointPanel, bpy.types.Panel):
    bl_label = "Physics Tools"
    bl_idname = "BP_PT_physics_panel"

    def draw(self, context):
        layout = self.layout
        physics_props = context.scene.bp_physics_properties
        bp_mass_groups = context.scene.bp_mass_object_groups

        row = layout.row()
        row.prop_search(physics_props, "selected_mog",
                        context.scene, "bp_mass_object_groups")
        row = layout.row()
        if is_in_collection_group(physics_props.selected_mog, bp_mass_groups):
            sel_mog = bp_mass_groups[physics_props.selected_mog]

            if sel_mog.use_com_object and sel_mog.com_object is not None and sel_mog.is_rig_pinned and sel_mog.pinned_rig is not None:
                row = layout.row()
                row.alignment = 'CENTER'
                row.label(text="Angular Velocity")

                if sel_mog.com_object.rotation_mode != 'AXIS_ANGLE':
                    row = row.row()
                    row.label(
                        text="Set the COM Object's rotation mode to 'Axis Angle'")
                else:
                    row = layout.row()
                    row.prop(physics_props, "show_com_object_axis")
                    row = layout.row()
                    row.prop(sel_mog.com_object,
                             "rotation_axis_angle", text="")
                    row = layout.row()
                    row.label(text="Moment of Inertia: ")
                    sub = row.row()
                    sub.alignment = 'RIGHT'
                    center_of_mass = get_com(sel_mog.mass_object_collection.all_objects)
                    current_axis = Vector((sel_mog.com_object.rotation_axis_angle[1], sel_mog.com_object.rotation_axis_angle[2], sel_mog.com_object.rotation_axis_angle[3]))
                    moment_of_inertia = get_moment_of_inertia(sel_mog.mass_object_collection.all_objects, center_of_mass, current_axis)
                    sub.label(text="{} kg·m2".format(
                        round(moment_of_inertia, 4)))

                    # Axis Alignment
                    row = layout.row()
                    row.alignment = 'CENTER'
                    row.label(text="Axis Alignment From Two Points")
                    row = layout.row()
                    row.prop(physics_props, "is_align_preview")
                    row.prop(physics_props, "point_scale")

                    # Left
                    split = layout.split()
                    col = split.column()
                    box = col.box()
                    row = box.row()
                    row.prop(physics_props, "align_rotation_p1")
                    row = box.row()
                    rp1 = row.operator(
                        "balance_point.referencepoint_set", text="Set Reference Point 1 From 3D Cursor")
                    rp1.target = 1

                    # Right
                    col = split.column()
                    box = col.box()
                    row = box.row()
                    row.prop(physics_props, "align_rotation_p2")
                    row = box.row()
                    rp2 = row.operator(
                        "balance_point.referencepoint_set", text="Set Reference Point 2 From 3D Cursor")
                    rp2.target = 2

                    # Align Axis
                    row = layout.row()
                    row.operator("balance_point.align_axis")

                    # Angular Velocity
                    row = layout.row()
                    row.alignment = 'CENTER'
                    row.label(text="Initial Angular Velocity")
                    row = layout.row()
                    row.prop(physics_props, "initial_angular_velocity")
                    row = layout.row()
                    center_of_mass = get_com(sel_mog.mass_object_collection.all_objects)
                    com_axis = Vector(
                        (sel_mog.com_object.rotation_axis_angle[1], sel_mog.com_object.rotation_axis_angle[2], sel_mog.com_object.rotation_axis_angle[3]))
                    moi = get_moment_of_inertia(
                        sel_mog.mass_object_collection.all_objects, center_of_mass, com_axis)
                    row.label(
                        text=f"Moment of Inertia: {str(round(moi, 4))} kg·m2")
                    row = layout.row()
                    row.operator("balance_point.calculate_angle_preview")

                    # Ballistics Curve
                    row = layout.row()
                    row.alignment = 'CENTER'
                    row.label(text="Ballistics Curve")
                    row = layout.row()
                    row.prop(physics_props, "is_ballistics_preview")
                    row = layout.row()
                    row.prop(physics_props, "ballistics_p1")
                    row = layout.row()
                    bp1 = row.operator("balance_point.referencepoint_set",
                                       text="Set Ballistics Reference Point From 3D Cursor")
                    bp1.target = 3
                    row = layout.row()
                    row.prop(physics_props, "gravity")
                    row = layout.row()
                    row.prop(physics_props, "time_of_flight")

                    # Bake
                    row = layout.row()
                    row.alignment = 'CENTER'
                    row.label(text="Frame Range")
                    row = layout.row()
                    row.prop(physics_props, "frame_start")
                    row = layout.row()
                    row.prop(physics_props, "frame_end")
                    row = layout.row()
                    row.prop(physics_props, "frame_rate")
                    row = layout.row()
                    row.label(
                        text=f"Duration: {physics_props.frame_end - physics_props.frame_start}")
                    row = layout.row()
                    row.operator("balance_point.bake_physics")
            else:
                row = layout.row()
                row.label(
                    text="Add a COM Object and a Pinned Rig to use the Physics Tools.")
