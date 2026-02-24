import bpy
from bpy.app.handlers import persistent
from mathutils import Vector
from .utils import get_com


@persistent
def update_mass_group_com(scene):
    bp_mass_groups = bpy.context.scene.bp_mass_object_groups

    for group in bp_mass_groups:
        if any(mass_collection is not None for mass_collection in group.mass_collections):
            com_location = get_com(group)

            group.com_location = com_location
            
            if group.com_object_enabled:
                group.com_object.matrix_world.translation = com_location

