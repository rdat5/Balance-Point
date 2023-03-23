import bpy

class BalancePointPanel(bpy.types.Panel):
    """Balance Point settings"""
    bl_label = "Balance Point Settings"
    bl_idname = "OBJECT_PT_balance_point_settings_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Balance Point"

    def draw(self, context):
        layout = self.layout
        com_props = context.scene.com_properties
        bp_mass_groups = context.scene.bp_mass_object_groups

        # Com Tracking On/Off
        row = layout.row(align=True)
        row.prop(com_props, "com_tracking_on")
        # Mass Object Groups
        row = layout.row(align=True)
        row.label(text="Mass Object Groups:")
        box = layout.box()
        for mass_group in bp_mass_groups:
            innerBox = box.box()
            row = innerBox.row(align=True)
            row.label(text="Mass Object Collection")
            row.prop(mass_group, "visible")
            row = innerBox.row(align=True)
            row.prop(mass_group, "mass_object_collection", text="")
            row.prop(mass_group, "color", text="")
            row = innerBox.row(align=True)
            row.prop(mass_group, "scale")
            row = innerBox.row(align=True)
            row.prop(mass_group, "line_to_floor")
            row.prop(mass_group, "com_floor_level")
            if mass_group.mass_object_collection is not None and com_props.com_tracking_on:
                cl = mass_group.com_location
                row = innerBox.row(align=True)
                cl = mass_group.com_location
                row.label(text="CoM Loc: (%.2f, %.2f, %.2f)" % (cl[0], cl[1], cl[2]))

        row = box.row()
        add_bp_group_text = 'Add' if len(bp_mass_groups) > 1 else 'Add Mass Object Group'
        row.operator("balance_point.massgroup_add", text=add_bp_group_text, icon="ADD")
        if len(bp_mass_groups) > 1:
            row.operator("balance_point.massgroup_remove", text="Remove", icon="REMOVE")

        # Update
        update_icon = 'PAUSE' if com_props.com_drawing_on else 'PLAY'
        update_text = 'Hide Markers' if com_props.com_drawing_on else 'Show Markers'

        row = layout.row(align=True)
        row.scale_y = 2.0
        row.operator("balance_point.toggle_drawing", text=update_text, icon=update_icon)


class MassPropertiesPanel(bpy.types.Panel):
    """Mass properties panel"""
    bl_label = "Mass Properties"
    bl_idname = "OBJECT_PT_mass_properties_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Balance Point"

    def draw(self, context):
        layout = self.layout
        sel_obj = context.selected_objects

        # Mass properties
        col = layout.column(align=True)

        row = col.row()
        row.label(text="Mass properties to selected")

        row = col.row(align=True)
        row.operator("balance_point.massprop_add", text="Add", icon='ADD')
        row.operator("balance_point.massprop_del", text="Remove", icon='REMOVE')

        # Volume
        col = layout.column(align=True)

        row = col.row()
        row.label(text="Volume")

        row = col.row()
        row.operator("balance_point.calculate_volume", icon='CUBE')

        # Object Origin to Center of Mass
        col = layout.column(align=True)

        row = col.row()
        row.label(text="Set Selected Origin(s) to Object CoM")

        row = col.row()
        row.operator("object.origin_set", text='Origin to Center of Mass (Volume)',
                     icon='DOT').type = 'ORIGIN_CENTER_OF_VOLUME'

        # Set active to selected
        col = layout.column(align=True)

        row = col.row()
        row.label(text="Set active to selected")

        row = col.row(align=True)
        row.operator("balance_point.set_active_true", icon='RADIOBUT_ON')
        row.operator("balance_point.set_active_false", icon='RADIOBUT_OFF')
        col.operator("balance_point.toggle_active", icon='ARROW_LEFTRIGHT')

        # Selected mass objects
        col = layout.column(align=True)

        row = col.row(align=True)
        row.label(text="Selected Mass Objects: ")
        for obj in sel_obj:
            if obj.get('volume') is not None:
                box = col.box()

                # split box
                split = box.split(factor=0.4)

                # left column
                col1 = split.column(align=True)
                col1.label(text="" + obj.name)

                # get if active
                if obj.get("active") == True:
                    col1.label(text="Active", icon='RADIOBUT_ON')
                elif obj.get("active") == False:
                    col1.label(text="Inactive", icon='RADIOBUT_OFF')

                # right column
                obj_mass = round(obj.get("density") * obj.get("volume") * obj.get("active"), 3)

                col2 = split.column(align=True)
                col2.prop(obj, '["density"]')
                col2.prop(obj, '["volume"]')
                col2.label(text="Mass: " + str(obj_mass))
        if len(sel_obj) > 0:
            row = layout.row()
            row.label(text="Total Mass of Selected: " + str(round(get_total_mass(sel_obj), 3)))


def get_total_mass(objects):
    total_mass = 0

    for obj in objects:
        if obj.get("active"):
            obj_mass = obj.get("density") * obj.get("volume")

            total_mass += obj_mass

    return total_mass