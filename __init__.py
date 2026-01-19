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
    BP_AddMassCollection,
    BP_RemoveMassCollection,
    AddMassObjectGroup,
    RemoveMassObjectGroup,
    SetReferencePoint,
    AlignAxisByPoints,
    BakeBPPhysics,
    BakeBPRootMotion,
    BP_AddControlBones,
    BP_DeleteControlBone,
    AlignAxisByCursor,
    AlignAxisByCursorRef,
    SetStartingPoint,
    SetStartingPointToCOM,
    SetReferencePointToCOM,
    CalculateBPMotionPath,
    ClearBPMotionPath,
)
from .mass_ops import (
    AddMassProps,
    RemoveMassProps,
    ToggleActiveProperty,
    SetActiveTrue,
    SetActiveFalse,
    CalculateVolume,
    SetDensity,
)
from .ui import (
    BP_UL_List,
    BP_PT_MainMenu,
    BP_PT_DrawSettings,
    BP_PT_PhysicsTools,
    BP_PT_ReferencePoints,
    BP_PT_RotationAxis,
    BP_PT_MassPropertyEditor,
    BP_PT_BallisticsRuler,
    BP_PT_Baking,
    BP_PT_Motion_Path,
    BP_PT_Root_Motion,
    BP_PT_MassSelected,
)
from .props import (
    BP_MotionPathPoint,
    BP_RootControlBones,
    BP_MassCollections,
    BPMassObjectGroup,
    BPComProperties,
)
from .center_of_mass import update_mass_group_com
import bpy
bl_info = {
    "name": "Balance Point",
    "author": "Ray Allen Datuin",
    "version": (3, 0, 0),
    "blender": (5, 0, 0),
    "location": "View3D > Sidebar > Balance Point",
    "description": "Visualizes the center of mass of collections of objects",
    "warning": "",
    "doc_url": "https://github.com/rdat5/balance-point/wiki",
    "category": "3D View",
}

draw_handler = None

# Class Registration


classes = (
    BP_AddMassCollection,
    BP_RemoveMassCollection,
    BP_MotionPathPoint,
    BP_MassCollections,
    BP_RootControlBones,
    BPMassObjectGroup,
    BPComProperties,
    BP_UL_List,
    BP_PT_MainMenu,
    BP_PT_Motion_Path,
    BP_PT_Root_Motion,
    BP_PT_DrawSettings,
    BP_PT_PhysicsTools,
    BP_PT_ReferencePoints,
    BP_PT_RotationAxis,
    BP_PT_BallisticsRuler,
    BP_PT_Baking,
    BP_PT_MassPropertyEditor,
    BP_PT_MassSelected,
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
    AlignAxisByCursorRef,
    BakeBPPhysics,
    BakeBPRootMotion,
    BP_AddControlBones,
    BP_DeleteControlBone,
    SetStartingPoint,
    SetStartingPointToCOM,
    SetReferencePointToCOM,
    CalculateBPMotionPath,
    ClearBPMotionPath,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.bp_com_properties = bpy.props.PointerProperty(
        type=BPComProperties)
    bpy.types.Scene.bp_mass_object_groups = bpy.props.CollectionProperty(
        type=BPMassObjectGroup)
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

    del bpy.types.Scene.bp_com_properties
    del bpy.types.Scene.bp_mass_object_groups
    del bpy.types.Scene.bp_group_index

    global draw_handler

    bpy.app.handlers.depsgraph_update_post.remove(update_mass_group_com)
    bpy.app.handlers.frame_change_post.remove(update_mass_group_com)
    bpy.types.SpaceView3D.draw_handler_remove(draw_handler, 'WINDOW')


if __name__ == "__main__":
    register()
