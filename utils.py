from mathutils import Vector, Matrix
import math

def is_valid_triangle(p1, p2, p3):
    import numpy as np
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
    import numpy as np
    v1 = np.array(p2) - np.array(p1)
    v2 = np.array(p3) - np.array(p1)
    normal = np.cross(v1, v2)
    return normal / np.linalg.norm(normal)


def get_total_mog_mass(group):
    total_mass = 0

    for mass_collection in group.mass_collections:
        if mass_collection.mass_object_collection is not None:
            for obj in mass_collection.mass_object_collection.all_objects:
                if obj.get("active"):
                    obj_mass = obj.get("density") * obj.get("volume")

                    total_mass += obj_mass

    return total_mass


def get_total_mass(objects):
    total_mass = 0

    for obj in objects:
        if obj.get("active"):
            obj_mass = obj.get("density") * obj.get("volume")

            total_mass += obj_mass

    return total_mass


def get_inertia_tensor(group, com_vector):
    I_xx, I_yy, I_zz = 0.0, 0.0, 0.0
    I_xy, I_xz, I_yz = 0.0, 0.0, 0.0

    for mass_collection in group.mass_collections:
        if mass_collection.mass_object_collection is not None:
            for obj in mass_collection.mass_object_collection.all_objects:
                if obj.get("active"):
                    m = obj.get("density") * obj.get("volume") * mass_collection.influence
                    

                    r = obj.matrix_world.translation - com_vector

                    x, y, z = r.x, r.y, r.z

                    I_xx += m * (y**2 + z**2)
                    I_yy += m * (x**2 + z**2)
                    I_zz += m * (x**2 + y**2)

                    I_xy -= m * (x * y)
                    I_xz -= m * (x * z)
                    I_yz -= m * (y * z)

    return Matrix((
        (I_xx, I_xy, I_xz),
        (I_xy, I_yy, I_yz),
        (I_xz, I_yz, I_zz)
    ))


def get_com(group):
    center_of_mass = Vector((0, 0, 0))

    total_mass = 0
    weighted_sum = Vector((0, 0, 0))

    for mass_collection in group.mass_collections:
        if mass_collection.mass_object_collection is not None:
            for obj in mass_collection.mass_object_collection.all_objects:
                if obj.get("active"):
                    obj_mass = obj.get("density") * obj.get("volume") * mass_collection.influence

                    total_mass += obj_mass
                    weighted_sum += (obj_mass * obj.matrix_world.translation)

    if total_mass > 0:
        center_of_mass = weighted_sum / total_mass

    return center_of_mass


def projectile_position_linear(start_pos, second_pos, gravity, time_of_flight, elapsed_time, drag_vector):
    x0, y0, z0 = start_pos
    x1, y1, z1 = second_pos
    
    kx, ky, kz = drag_vector
    
    T = time_of_flight
    t = elapsed_time
    g = gravity
    
    if kx < 1e-5:
        v0x = (x1 - x0) / T
        x = x0 + v0x * t
    else:
        den_x = 1.0 - math.exp(-kx * T)
        loss_tx = 1.0 - math.exp(-kx * t)
        v0x = (kx * (x1 - x0)) / den_x
        x = x0 + (v0x / kx) * loss_tx

    if ky < 1e-5:
        v0y = (y1 - y0) / T
        y = y0 + v0y * t
    else:
        den_y = 1.0 - math.exp(-ky * T)
        loss_ty = 1.0 - math.exp(-ky * t)
        v0y = (ky * (y1 - y0)) / den_y
        y = y0 + (v0y / ky) * loss_ty

    if kz < 1e-5:
        v0z = (z1 - z0) / T + 0.5 * g * T
        z = z0 + v0z * t - 0.5 * g * t**2
    else:
        den_z = 1.0 - math.exp(-kz * T)
        loss_tz = 1.0 - math.exp(-kz * t)
        v0z = (kz * (z1 - z0) + g * T) / den_z - (g / kz)
        z = z0 + ((v0z + g / kz) / kz) * loss_tz - (g * t) / kz

    return Vector((x, y, z))