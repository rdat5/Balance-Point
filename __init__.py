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
from .bp_ops import (
    AddMassObjectGroup,
    RemoveMassObjectGroup,
    SetReferencePoint,
    AlignAxisByPoints,
    BakeBPPhysics,
    CalculateAnglePreview,
    AlignAxisByCursor,
    SetStartingPoint,
    SetStartingPointToCOM,
    ClearAnglePreview,
    SetReferencePointToCOM
)
from .mass_ops import (
    AddMassProps,
    RemoveMassProps,
    ToggleActiveProperty,
    SetActiveTrue,
    SetActiveFalse,
    CalculateVolume,
    SetDensity
)
from .ui import *
from .props import *
from .center_of_mass import update_mass_group_com
import bpy
bl_info = {
    "name": "Balance Point",
    "author": "Ray Allen Datuin",
    "version": (2, 0, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Balance Point",
    "description": "Visualizes the center of mass of collections of objects",
    "warning": "",
    "doc_url": "https://github.com/rdat5/balance-point/wiki",
    "category": "3D View",
}

draw_handler = None

# Class Registration


classes = (
    CalculatedMOI,
    MassObjectGroup,
    ComProperties,
    BP_UL_List,
    BP_PT_MainMenu,
    BP_PT_MassPropertyEditor,
    BP_PT_MassSelected,
    CalculateAnglePreview,
    PhysicsProperties,
    AddMassObjectGroup,
    RemoveMassObjectGroup,
    AddMassProps,
    RemoveMassProps,
    ToggleActiveProperty,
    SetActiveTrue,
    SetActiveFalse,
    CalculateVolume,
    SetDensity,
    SetReferencePoint,
    AlignAxisByCursor,
    AlignAxisByPoints,
    BakeBPPhysics,
    SetStartingPoint,
    SetStartingPointToCOM,
    ClearAnglePreview,
    SetReferencePointToCOM
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.com_properties = bpy.props.PointerProperty(
        type=ComProperties)
    bpy.types.Scene.bp_mass_object_groups = bpy.props.CollectionProperty(
        type=MassObjectGroup)
    bpy.types.Scene.bp_physics_properties = bpy.props.PointerProperty(
        type=PhysicsProperties)
    bpy.types.Scene.bp_group_index = bpy.props.IntProperty(
        name="Active Index")

    global draw_handler

    bpy.app.handlers.depsgraph_update_post.append(update_mass_group_com)
    bpy.app.handlers.frame_change_post.append(update_mass_group_com)
    draw_handler = bpy.types.SpaceView3D.draw_handler_add(
        draw_bp, (None, None), 'WINDOW', 'POST_VIEW')


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.com_properties
    del bpy.types.Scene.bp_mass_object_groups
    del bpy.types.Scene.bp_physics_properties
    del bpy.types.Scene.bp_group_index

    global draw_handler

    bpy.app.handlers.depsgraph_update_post.remove(update_mass_group_com)
    bpy.app.handlers.frame_change_post.remove(update_mass_group_com)
    bpy.types.SpaceView3D.draw_handler_remove(draw_handler, 'WINDOW')


if __name__ == "__main__":
    register()
