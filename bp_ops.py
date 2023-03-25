import bpy

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
        bpy.context.scene.bp_mass_object_groups.add()
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