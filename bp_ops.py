import bpy
import numpy as np

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
        new_item = bpy.context.scene.bp_mass_object_groups.add()
        new_item.name = f"Mass Object Group {len(bpy.context.scene.bp_mass_object_groups)}"
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


class SetReferencePoint(bpy.types.Operator):
    """Sets the coordinate of a reference point."""
    bl_idname = "balance_point.referencepoint_set"
    bl_label = "Set Reference Point From 3D Cursor"

    target: bpy.props.IntProperty(name="Reference point being set.")

    def execute(self, context):
        physics_props = context.scene.bp_physics_properties

        cursor_loc = context.scene.cursor.location
        cursor_coords = [cursor_loc[0], cursor_loc[1], cursor_loc[2]]

        match self.target:
            case 1:
                physics_props.align_rotation_p1 = cursor_coords
            case 2: 
                physics_props.align_rotation_p2 = cursor_coords
        return {'FINISHED'}


class AlignAxisByPoints(bpy.types.Operator):
    """Aligns COM Object's rotation axis about two reference points."""
    bl_idname = "balance_point.align_axis"
    bl_label = "Align COM Object's Axis"

    @classmethod
    def poll(cls, context):
        physics_props = context.scene.bp_physics_properties
        sel_mog = context.scene.bp_mass_object_groups[physics_props.selected_mog]

        p1 = physics_props.align_rotation_p1
        p2 = physics_props.align_rotation_p2
        p3 = sel_mog.com_object.matrix_world.translation
        return is_valid_triangle(p1, p2, p3)

    def execute(self, context):
        physics_props = context.scene.bp_physics_properties
        com_obj = context.scene.bp_mass_object_groups[physics_props.selected_mog].com_object

        p1 = physics_props.align_rotation_p1
        p2 = physics_props.align_rotation_p2
        p3 = com_obj.matrix_world.translation
        norm = get_triangle_normal(p1, p2, p3)
        com_obj.rotation_axis_angle[1] = norm[0]
        com_obj.rotation_axis_angle[2] = norm[1]
        com_obj.rotation_axis_angle[3] = norm[2]
        return {'FINISHED'}


def is_valid_triangle(p1, p2, p3):
    A = np.array([p1[0], p1[1], p1[2]])
    B = np.array([p2[0], p2[1], p2[2]])
    C = np.array([p3[0], p3[1], p3[2]])
    
    v1 = B - C
    v2 = A - C
    cross_product = np.cross(v1, v2)
    if np.allclose(cross_product, 0):
        return False
    return True


def get_triangle_normal(p1, p2, p3):
    v1 = np.array(p2) - np.array(p1)
    v2 = np.array(p3) - np.array(p1)
    normal = np.cross(v1, v2)
    return normal / np.linalg.norm(normal)  # Normalize the normal vector