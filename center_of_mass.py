import bpy
from bpy.app.handlers import persistent
from mathutils import Vector

def get_com(objects):
    center_of_mass = Vector((0, 0, 0))

    total_mass = 0
    weighted_sum = Vector((0, 0, 0))

    for obj in objects:
        if obj.get("active"):
            obj_mass = obj.get("density") * obj.get("volume")

            total_mass += obj_mass
            weighted_sum += (obj_mass * obj.matrix_world.translation)

    if total_mass > 0:
        center_of_mass = weighted_sum / total_mass

    return center_of_mass


def combine_coll_objects(collections):
    combined_objects = []

    for coll in collections:
        for obj in coll.all_objects:
            combined_objects.append(obj)
    
    return combined_objects

@persistent
def update_mass_group_com(scene):
    com_props = bpy.context.scene.com_properties
    bp_mass_groups = bpy.context.scene.bp_mass_object_groups

    if com_props.com_tracking_on and len(bp_mass_groups) > 0:
        for mass_group in bp_mass_groups:
            if mass_group.mass_object_collection is not None:
                if mass_group.is_rig_pinned and mass_group.use_com_object and mass_group.pinned_rig is not None and mass_group.com_object is not None:
                    difference = get_com(combine_coll_objects([mass_group.mass_object_collection])) - mass_group.com_object.matrix_world.translation
                    mass_group.com_location = [mass_group.com_object.matrix_world.translation.x, mass_group.com_object.matrix_world.translation.y, mass_group.com_object.matrix_world.translation.z]
                    if difference.length > 0.0001:
                        mass_group.pinned_rig.matrix_world.translation -= difference
                else:    
                    mgc = get_com(combine_coll_objects([mass_group.mass_object_collection]))
                    mass_group.com_location = [mgc.x, mgc.y, mgc.z]
                    
                    if mass_group.use_com_object and mass_group.com_object is not None:
                        mass_group.com_object.matrix_world.translation = mgc
