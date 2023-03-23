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

from .draw import draw_bp
from .bp_ops import ToggleDrawing
from .mass_ops import (AddMassObjectGroup, RemoveMassObjectGroup, AddMassProps, RemoveMassProps,
                       ToggleActiveProperty, ToggleActiveProperty, SetActiveTrue, SetActiveFalse, CalculateVolume)
from .ui import BalancePointPanel, MassPropertiesPanel
from .props import *
from .center_of_mass import update_mass_group_com
import bpy
from mathutils import Vector
from bpy.app.handlers import depsgraph_update_post
from bpy.app.handlers import frame_change_post
from bpy.app import driver_namespace
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


HANDLER_KEY = "BP_UPDATE_FN"


def initialize_bp_mass_groups():
    bpy.context.scene.bp_mass_object_groups.clear()
    bpy.context.scene.bp_mass_object_groups.add()

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
