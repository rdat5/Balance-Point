import bpy
from bpy.app.handlers import persistent
from mathutils import Vector

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


@persistent
def update_mass_group_com(scene):
    com_props = bpy.context.scene.com_properties
    bp_mass_groups = bpy.context.scene.bp_mass_object_groups

    if com_props.com_tracking_on and len(bp_mass_groups) > 0:
        for mass_group in bp_mass_groups:
            if mass_group.mass_object_collection is not None:
                mgc = get_com(mass_group.mass_object_collection)
                mass_group.com_location = [mgc.x, mgc.y, mgc.z]