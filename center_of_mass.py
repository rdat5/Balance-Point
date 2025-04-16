import bpy
from bpy.app.handlers import persistent
from mathutils import Vector
from .utils import get_com


@persistent
def update_mass_group_com(scene):
    bp_mass_groups = bpy.context.scene.bp_mass_object_groups

    for group in bp_mass_groups:
        if group.mass_object_collection is not None:
            if not group.is_rig_pinned:
                group.com_location = get_com(
                    group.mass_object_collection.all_objects)
            else:
                if group.pinned_rig is not None:
                    difference = get_com(
                        group.mass_object_collection.all_objects) - Vector(group.com_location)
                    if difference.length > 0.0001:
                        group.pinned_rig.location -= difference
    pass
