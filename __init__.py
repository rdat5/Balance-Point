# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Balance Point",
    "author": "Ray Allen Datuin",
    "version": (1, 1, 0),
    "blender": (3, 4, 0),
    "location": "View3D > Sidebar > Balance Point",
    "description": "Visualizes the center of mass of collections of objects",
    "warning": "",
    "doc_url": "https://github.com/rdat5/balance-point/wiki",
    "category": "3D View",
}


from bpy.app.handlers import persistent
from bpy.app import driver_namespace
from bpy.app.handlers import frame_change_post
from bpy.app.handlers import depsgraph_update_post
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
import bmesh
import gpu
import bpy

from .shapes import *
from .props import *
from .ui import BalancePointPanel, MassPropertiesPanel

# Const

HANDLER_KEY = "BP_UPDATE_FN"

# Shader setup

shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')

# Classes


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

    def execute(self, context):
        if len(bpy.context.scene.bp_mass_object_groups) > 1:
            bpy.context.scene.bp_mass_object_groups.remove(len(bpy.context.scene.bp_mass_object_groups) - 1)
        return {'FINISHED'}


class AddMassProps(bpy.types.Operator):
    """Add mass properties to selected objects"""
    bl_idname = "balance_point.massprop_add"
    bl_label = "Add mass properties to selected"

    def execute(self, context):
        sel_obj = context.selected_objects

        for obj in sel_obj:
            if obj.type == 'MESH':
                if obj.get('active') is None:
                    obj["active"] = True
                if obj.get('density') is None:
                    obj["density"] = 1.0
                if obj.get('volume') is None:
                    obj["volume"] = 1.0
        return {'FINISHED'}


class RemoveMassProps(bpy.types.Operator):
    """Remove mass properties from selected objects"""
    bl_idname = "balance_point.massprop_del"
    bl_label = "Remove mass properties from selected"

    def execute(self, context):
        sel_obj = context.selected_objects

        for obj in sel_obj:
            if obj.type == 'MESH':
                if obj.get('active') is not None:
                    del obj["active"]
                if obj.get('density') is not None:
                    del obj["density"]
                if obj.get('volume') is not None:
                    del obj["volume"]
        return {'FINISHED'}


class ToggleActiveProperty(bpy.types.Operator):
    """Toggles the active property"""
    bl_idname = "balance_point.toggle_active"
    bl_label = "Toggle Active"

    def execute(self, context):
        sel_obj = context.selected_objects

        for obj in sel_obj:
            if obj.get('active') is not None:
                set_active(obj, (not obj['active']))
        return {'FINISHED'}


class SetActiveTrue(bpy.types.Operator):
    """Toggles the active property"""
    bl_idname = "balance_point.set_active_true"
    bl_label = "Active"

    def execute(self, context):
        sel_obj = context.selected_objects

        for obj in sel_obj:
            if obj.get('active') is not None:
                set_active(obj, True)
        return {'FINISHED'}


class SetActiveFalse(bpy.types.Operator):
    """Toggles the active property"""
    bl_idname = "balance_point.set_active_false"
    bl_label = "Inactive"

    def execute(self, context):
        sel_obj = context.selected_objects

        for obj in sel_obj:
            if obj.get('active') is not None:
                set_active(obj, False)
        return {'FINISHED'}


class CalculateVolume(bpy.types.Operator):
    """Calculate volume of selected"""
    bl_idname = "balance_point.calculate_volume"
    bl_label = "Calculate volume of selected"

    def execute(self, context):
        sel_obj = context.selected_objects

        for obj in sel_obj:
            if obj.get('volume') is not None and obj.type == 'MESH':
                obj['volume'] = get_volume(obj)
        return {'FINISHED'}


class ToggleDrawing(bpy.types.Operator):
    """Adds/Removes center of mass render function from draw handler"""
    bl_idname = "balance_point.toggle_drawing"
    bl_label = "Toggle Drawing"

    def execute(self, context):
        com_props = context.scene.com_properties

        com_props.com_drawing_on = not com_props.com_drawing_on
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        return {'FINISHED'}


def set_active(obj, act):
    obj['active'] = act
    if act == True:
        obj.display_type = 'SOLID'
    elif act == False:
        obj.display_type = 'WIRE'


def get_volume(obj):
    volume = 0.0

    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    me = obj_eval.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    obj_eval.to_mesh_clear()
    volume = bm.calc_volume()
    bm.free()

    return volume


def get_com(coll):
    center_of_mass = Vector((0, 0, 0))

    total_mass = 0
    weighted_sum = Vector((0, 0, 0))

    for obj in coll.all_objects:
        if obj.get("active"):
            obj_mass = obj.get("density") * obj.get("volume")

            total_mass += obj_mass
            weighted_sum += (obj_mass * obj.matrix_world.translation)

    if total_mass > 0:
        center_of_mass = weighted_sum / total_mass

    return center_of_mass


def transform_indices(vertices, scale, translate_vector):
    new_vertices = []
    for v in vertices:
        new_vertices.append((
            (v[0] * scale) + translate_vector.x,
            (v[1] * scale) + translate_vector.y,
            (v[2] * scale) + translate_vector.z
        ))
    return new_vertices


def get_final_com_shape(group):
    group_com_loc = Vector((group.com_location[0], group.com_location[1], group.com_location[2]))
    group_com_floor_loc = Vector((group_com_loc.x, group_com_loc.y, group.com_floor_level))
    com_shape = transform_indices(SHAPE_COM_MARKER, group.scale, group_com_loc)
    com_floor_shape = transform_indices(SHAPE_FLOOR_MARKER, group.scale, group_com_floor_loc)
    final_shape = com_shape + com_floor_shape
    if group.line_to_floor:
        final_shape += (group_com_loc.to_tuple(), group_com_floor_loc.to_tuple())
    return final_shape


def draw_bp(self, context):
    com_props = bpy.context.scene.com_properties
    bp_mass_groups = bpy.context.scene.bp_mass_object_groups
    # Go through each collection, create a batch, render it
    if com_props.com_drawing_on:
        for group in bp_mass_groups:
            if group.visible:
                # Get color
                shader.uniform_float("color", (group.color.r, group.color.g, group.color.b, 1.0))
                # Get shape vertices
                batch = batch_for_shader(shader, 'LINES', {"pos": get_final_com_shape(group)})
                batch.draw(shader)


def initialize_bp_mass_groups():
    bpy.context.scene.bp_mass_object_groups.clear()
    bpy.context.scene.bp_mass_object_groups.add()

@persistent
def update_mass_group_com(scene):
    com_props = bpy.context.scene.com_properties
    bp_mass_groups = bpy.context.scene.bp_mass_object_groups

    if com_props.com_tracking_on:
        for mass_group in bp_mass_groups:
            if mass_group.mass_object_collection is not None:
                mgc = get_com(mass_group.mass_object_collection)
                mass_group.com_location = [mgc.x, mgc.y, mgc.z]

# Class Registration


classes = (
    MassObjectGroup,
    ComProperties,
    BalancePointPanel,
    MassPropertiesPanel,
    AddMassObjectGroup,
    RemoveMassObjectGroup,
    AddMassProps,
    RemoveMassProps,
    ToggleActiveProperty,
    SetActiveTrue,
    SetActiveFalse,
    CalculateVolume,
    ToggleDrawing
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.com_properties = bpy.props.PointerProperty(type=ComProperties)
    bpy.types.Scene.bp_mass_object_groups = bpy.props.CollectionProperty(type=MassObjectGroup)
    bpy.app.timers.register(initialize_bp_mass_groups, first_interval=0.1)

    # Add depsgraph, frame_change handler callbacks
    if HANDLER_KEY not in driver_namespace:
        depsgraph_update_post.append(update_mass_group_com)
        frame_change_post.append(update_mass_group_com)
        driver_namespace[HANDLER_KEY] = update_mass_group_com

    bpy.types.SpaceView3D.draw_handler_add(
                draw_bp, (None, None), 'WINDOW', 'POST_VIEW')

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.com_properties
    del bpy.types.Scene.bp_mass_object_groups

    # Remove depsgraph, frame_change handler callbacks
    if HANDLER_KEY in driver_namespace:
        if driver_namespace[HANDLER_KEY] in depsgraph_update_post:
            depsgraph_update_post.remove(driver_namespace[HANDLER_KEY])
            frame_change_post.remove(driver_namespace[HANDLER_KEY])


if __name__ == "__main__":
    register()
