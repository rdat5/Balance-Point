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

