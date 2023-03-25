import bpy

class BalancePointPanel(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Balance Point"

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
        row.prop(com_props, "com_tracking_on", toggle=1, icon=track_icon, text="CoM Tracking " + track_text)

        draw_icon = 'HIDE_OFF' if com_props.com_drawing_on else 'HIDE_ON'
        draw_text = 'Enabled' if com_props.com_drawing_on else 'Disabled'
        row.prop(com_props, "com_drawing_on", toggle=1, icon=draw_icon, text="CoM Drawing " + draw_text)


class BP_PT_mass_object_groups(BalancePointPanel, bpy.types.Panel):
    bl_parent_id = "BP_PT_Main"
    bl_label = "Mass Object Groups"

    def draw(self, context):
        layout = self.layout
        bp_mass_groups = context.scene.bp_mass_object_groups

        for group in bp_mass_groups:
            box = layout.box()
            split = box.split(factor=0.1)
            # left
            col = split.column()
            col.scale_y = 4.0
            viz_icon = 'HIDE_OFF' if group.visible else 'HIDE_ON'
            col.prop(group, "visible", toggle=1, icon=viz_icon, text="")

            # right
            col = split.column()
            row = col.row()
            row.use_property_decorate = False
            row.prop(group, "mass_object_collection", text="Mass Objects")
            row = col.row(align=True)
            row.prop(group, "scale")
            row.scale_x = 0.3
            row.prop(group, "color", text="")
            row = col.row()
            row.prop(group, "com_floor_level")
            sub = row.row()
            sub.alignment = 'RIGHT'
            sub.prop(group, "line_to_floor")
            row = col.row()
            row.label(text="Center of Mass:")
            sub = row.row()
            sub.alignment = 'RIGHT'
            gcm = group.com_location
            sub.label(text="({}, {}, {})".format(round(gcm[0], 4), round(gcm[1], 4), round(gcm[2], 4)))
            row = col.row()
        
        if len(bp_mass_groups) > 1:
            row = layout.row()
            row.operator('balance_point.massgroup_remove', icon='REMOVE')
        row = layout.row()
        row.scale_y = 1.5
        row.operator('balance_point.massgroup_add', icon='ADD')

class MassPropertiesPanel(BalancePointPanel, bpy.types.Panel):
    """Mass properties panel"""
    bl_label = "Mass Property Editing"
    bl_idname = "BP_PT_mass_editing_panel"

    def draw(self, context):
        layout = self.layout
        sel_obj = context.selected_objects

        row = layout.row()
        row.alignment = 'CENTER'
        row.label(text="Mass Properties")
        row = layout.row()
        row.operator("balance_point.massprop_add", text="Add", icon='ADD')
        row.operator("balance_point.massprop_del", text="Remove", icon='REMOVE')
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
    bl_label = "Mass Object Groups"

    def draw(self, context):
        layout = self.layout
        sel_obj = context.selected_objects

        row = layout.row()
        row.alignment = 'RIGHT'
        row.label(text="Total Mass: {} kg".format(round(get_total_mass(sel_obj), 4)))

        for obj in sel_obj:
            if obj.get('volume') is not None:
                box = layout.box()

                row = box.row()
                obj_active = 'RADIOBUT_ON' if obj.get('active') else 'RADIOBUT_OFF'
                row.label(text="", icon=obj_active)
                row.label(text=obj.name)
                sub = row.row()
                sub.alignment = 'RIGHT'
                obj_mass = round(obj.get("density") * obj.get("volume") * obj.get("active"), 4)
                sub.label(text="Mass: {} kg".format(obj_mass))
                
                row = box.row()
                row.prop(obj, '["density"]')
                row.prop(obj, '["volume"]')


def get_total_mass(objects):
    total_mass = 0

    for obj in objects:
        if obj.get("active"):
            obj_mass = obj.get("density") * obj.get("volume")

            total_mass += obj_mass

    return total_mass