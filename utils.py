from mathutils import Vector, Matrix


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


def get_total_mass(objects):
    total_mass = 0

    for obj in objects:
        if obj.get("active"):
            obj_mass = obj.get("density") * obj.get("volume")

            total_mass += obj_mass

    return total_mass


def get_inertia_tensor(objects, center_of_mass):
    import numpy as np
    I_xx = I_yy = I_zz = I_xy = I_xz = I_yz = 0.0
    
    com_np = np.array(center_of_mass)

    for obj in objects:
        if obj.get("active"):
            pos_world = np.array(obj.matrix_world.translation)
            r = pos_world - com_np
            
            x, y, z = r[0], r[1], r[2]
            
            mass = obj.get("density") * obj.get("volume")
            
            I_xx += mass * (y*y + z*z)
            I_yy += mass * (x*x + z*z)
            I_zz += mass * (x*x + y*y)
            
            I_xy -= mass * (x * y)
            I_xz -= mass * (x * z)
            I_yz -= mass * (y * z)

    tensor = Matrix([
        [I_xx, I_xy, I_xz],
        [I_xy, I_yy, I_yz],
        [I_xz, I_yz, I_zz]
    ])
    
    return tensor


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


def projectile_position(start_pos, second_pos, gravity, time_of_flight, elapsed_time):
    x0, y0, z0 = start_pos
    x1, y1, z1 = second_pos

    v0x = (x1 - x0) / time_of_flight
    v0y = (y1 - y0) / time_of_flight
    v0z = (z1 - z0) / time_of_flight + 0.5 * gravity * time_of_flight

    x = x0 + v0x * elapsed_time
    y = y0 + v0y * elapsed_time
    z = z0 + v0z * elapsed_time - 0.5 * gravity * elapsed_time**2

    return Vector((x, y, z))
