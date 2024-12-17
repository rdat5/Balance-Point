import bpy
import numpy
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


def get_moment_of_inertia(objects, center_of_mass, axis_vector):
    # Normalize
    axis_vector = numpy.array(axis_vector)
    axis_unit = axis_vector / numpy.linalg.norm(axis_vector)

    moment_of_inertia = 0.0

    for obj in objects:
        if obj.get("active"):
            position = obj.matrix_world.translation - Vector((center_of_mass[0], center_of_mass[1], center_of_mass[2]))
            mass = obj.get("density") * obj.get("volume")

            # Calculate perpendicular distance to the axis
            projection = numpy.dot(position, axis_unit) * axis_unit
            perpendicular_vector = position - Vector((projection[0], projection[1], projection[2]))
            perpendicular_distance_squared = numpy.dot(perpendicular_vector, perpendicular_vector)

            # Contribution to moment of inertia
            moment_of_inertia += mass * perpendicular_distance_squared
    
    return moment_of_inertia

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
                    # Moment of Inertia
                    com_object_axis = Vector((mass_group.com_object.rotation_axis_angle[1], mass_group.com_object.rotation_axis_angle[2], mass_group.com_object.rotation_axis_angle[3]))
                    mass_group.moment_of_inertia = get_moment_of_inertia(mass_group.mass_object_collection.all_objects, mass_group.com_location, com_object_axis)
                else:
                    included_objects = [mass_group.mass_object_collection]
                    if mass_group.include_secondary_collection and mass_group.secondary_mass_object_collection is not None:
                        included_objects.append(mass_group.secondary_mass_object_collection)
                    mgc = get_com(combine_coll_objects(included_objects))
                    mass_group.com_location = [mgc.x, mgc.y, mgc.z]
                    
                    if mass_group.use_com_object and mass_group.com_object is not None:
                        mass_group.com_object.matrix_world.translation = mgc
