import numpy as np
from mathutils import Vector

def is_valid_triangle(p1, p2, p3):
    A = np.array([p1[0], p1[1], p1[2]])
    B = np.array([p2[0], p2[1], p2[2]])
    C = np.array([p3[0], p3[1], p3[2]])
    
    v1 = B - C
    v2 = A - C
    cross_product = np.cross(v1, v2)
    if np.allclose(cross_product, 0):
        return False
    return True


def get_triangle_normal(p1, p2, p3):
    v1 = np.array(p2) - np.array(p1)
    v2 = np.array(p3) - np.array(p1)
    normal = np.cross(v1, v2)
    return normal / np.linalg.norm(normal)  # Normalize the normal vector


def get_total_mass(objects):
    total_mass = 0

    for obj in objects:
        if obj.get("active"):
            obj_mass = obj.get("density") * obj.get("volume")

            total_mass += obj_mass

    return total_mass


def is_in_collection_group(key, collection):
    for item in collection:
        if item.name == key:
            return True
    return False


def get_moment_of_inertia(objects, center_of_mass, axis_vector):
    # Normalize
    axis_vector = np.array(axis_vector)
    axis_unit = axis_vector / np.linalg.norm(axis_vector)

    moment_of_inertia = 0.0

    for obj in objects:
        if obj.get("active"):
            position = obj.matrix_world.translation - Vector((center_of_mass[0], center_of_mass[1], center_of_mass[2]))
            mass = obj.get("density") * obj.get("volume")

            # Calculate perpendicular distance to the axis
            projection = np.dot(position, axis_unit) * axis_unit
            perpendicular_vector = position - Vector((projection[0], projection[1], projection[2]))
            perpendicular_distance_squared = np.dot(perpendicular_vector, perpendicular_vector)

            # Contribution to moment of inertia
            moment_of_inertia += mass * perpendicular_distance_squared
    
    return moment_of_inertia


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