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
from mathutils import Vector
import bpy

from .props import *
from .ui import BalancePointPanel, MassPropertiesPanel
from .mass_ops import AddMassObjectGroup, RemoveMassObjectGroup, AddMassProps, RemoveMassProps, ToggleActiveProperty, ToggleActiveProperty, SetActiveTrue, SetActiveFalse, CalculateVolume
from .bp_ops import ToggleDrawing
from .draw import draw_bp

# Const

HANDLER_KEY = "BP_UPDATE_FN"

# Shader setup

# Classes


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
