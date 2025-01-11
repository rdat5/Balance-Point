import bpy
# import numpy
from bpy.app.handlers import persistent
from mathutils import Vector
from .utils import get_com, combine_coll_objects

@persistent
def update_mass_group_com(scene):
    com_props = bpy.context.scene.com_properties
    bp_mass_groups = bpy.context.scene.bp_mass_object_groups

    if com_props.com_tracking_on and len(bp_mass_groups) > 0:
        for mass_group in bp_mass_groups:
            if mass_group.mass_object_collection is not None:
                if mass_group.is_rig_pinned and mass_group.use_com_object and mass_group.pinned_rig is not None and mass_group.com_object is not None and not mass_group.include_secondary_collection:
                    included_objects = [mass_group.mass_object_collection]
                    difference = get_com(combine_coll_objects(included_objects)) - mass_group.com_object.matrix_world.translation
                    mass_group.com_location = [mass_group.com_object.matrix_world.translation.x, mass_group.com_object.matrix_world.translation.y, mass_group.com_object.matrix_world.translation.z]
                    if difference.length > 0.0001:
                        mass_group.pinned_rig.matrix_world.translation -= difference
                else:
                    included_objects = [mass_group.mass_object_collection]
                    if mass_group.include_secondary_collection and mass_group.secondary_mass_object_collection is not None:
                        included_objects.append(mass_group.secondary_mass_object_collection)
                    mgc = get_com(combine_coll_objects(included_objects))
                    mass_group.com_location = [mgc.x, mgc.y, mgc.z]
                    
                    if mass_group.use_com_object and mass_group.com_object is not None:
                        mass_group.com_object.matrix_world.translation = mgc
