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
                if group.com_object_enabled:
                    group.com_object.matrix_world.translation = get_com(group.mass_object_collection.all_objects)
            else:
                if group.pinned_rig is not None and group.root_bone != '':
                    group_com = get_com(
                        group.mass_object_collection.all_objects)
                    difference = group_com - Vector(group.com_location)
                    if difference.length > 0.0001:
                        group.pinned_rig.pose.bones[group.root_bone].location -= Vector(
                            (difference.x * group.pin_xyz[0], difference.y * group.pin_xyz[1], difference.z * group.pin_xyz[2]))
