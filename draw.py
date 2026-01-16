import bpy
import gpu
import numpy
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from .utils import (
    projectile_position,
    get_com,
)
from .shapes import SHAPE_FLOOR_MARKER

shader = gpu.shader.from_builtin('POINT_UNIFORM_COLOR')

def draw_bp(self, context):
    com_props = bpy.context.scene.bp_com_properties
    bp_mass_groups = bpy.context.scene.bp_mass_object_groups

    if not com_props.com_drawing_on or len(bp_mass_groups) == 0:
        return
    
    for group in bp_mass_groups:
        if not group.visible:
            continue

        has_mass_objects = any(mc is not None for mc in group.mass_collections)

        if has_mass_objects:
            group_com = get_com(group)

            draw_com_markers(group, group_com, com_props)
            draw_rotation_axis(group, group_com)
            draw_motion_path(group, com_props)

        draw_reference_points(group, com_props)
        draw_ballistics_ruler(group, com_props)

def draw_motion_path(group, com_props):
    if len(
            group.motion_path_points) > 0 and any(mass_collection is not None for mass_collection in group.mass_collections):
        point_positions = []

        # Get Points
        for path_point in group.motion_path_points:
            point_loc = path_point.point_location
            point_positions.append(
                Vector((point_loc[0], point_loc[1], point_loc[2])))

        # Draw lines
        for index, point_position in enumerate(
                point_positions):
            line_batch = []
            line_color = (1.0, 0.0, 0.0, 1.0) if index + \
                group.frame_start <= bpy.context.scene.frame_current else (0.0, 1.0, 0.0, 1.0)
            shader.uniform_float("color", line_color)
            point_coordinate = (
                point_position[0], point_position[1], point_position[2])

            if index > 0:
                previous_coordinate = point_positions[index - 1]
                line_batch += [(previous_coordinate[0],
                                previous_coordinate[1], previous_coordinate[2])]
                line_batch += [(point_coordinate[0],
                                point_coordinate[1], point_coordinate[2])]

            batch = batch_for_shader(
                shader, 'LINES', {"pos": line_batch})
            batch.draw(shader)

        # Draw Points
        for index, point_position in enumerate(
                point_positions):
            shader.uniform_float("color", (0.0, 0.0, 0.0, 1.0))
            gpu.state.point_size_set(
                com_props.motion_path_point_size)
            batch = batch_for_shader(
                shader, 'POINTS', {"pos": point_positions})
            batch.draw(shader)

def draw_reference_points(group, com_props):
    if group.show_reference_point:
        # Reference Point
        gpu.state.point_size_set(
            com_props.reference_point_size)
        shader.uniform_float(
            "color", (group.reference_color.r, group.reference_color.g, group.reference_color.b, 1.0))
        batch = batch_for_shader(
            shader, 'POINTS', {"pos": [Vector(group.reference_point)]})
        batch.draw(shader)

        # Ballistics Starting Point
        shader.uniform_float(
            "color", (group.ballistics_starting_point_color.r, group.ballistics_starting_point_color.g, group.ballistics_starting_point_color.b, 1.0))
        batch = batch_for_shader(
            shader, 'POINTS', {"pos": [Vector(group.ballistics_starting_point)]})
        batch.draw(shader)

def draw_rotation_axis(group, group_com):
    if group.show_axis:
        axis_verts = []

        cx = group.initial_axis.x
        cy = group.initial_axis.y
        cz = group.initial_axis.z
        axis_vector = numpy.array([cx, cy, cz])
        axis_unit = axis_vector / \
            numpy.linalg.norm(axis_vector)
        axis_verts += transform_indices([(-axis_unit[0], -axis_unit[1], -axis_unit[2]), (
            axis_unit[0], axis_unit[1], axis_unit[2])], 2.0, group_com)
        batch = batch_for_shader(
            shader, 'LINES', {"pos": axis_verts})
        batch = batch_for_shader(
            shader, 'LINES', {"pos": axis_verts})
        batch.draw(shader)

def draw_com_markers(group, group_com, com_props):
    # Get color
    shader.uniform_float(
        "color", (group.color.r, group.color.g, group.color.b, 1.0))

    # Draw COM Shape
    gpu.state.point_size_set(com_props.com_point_size)
    batch = batch_for_shader(
        shader, 'POINTS', {"pos": [group_com]})
    batch.draw(shader)

    # Draw Floor COM
    if com_props.floor_com_size > 0.0:
        floor_com_location = Vector(
            (group_com[0], group_com[1], group.com_floor_level))
        floor_com_verts = transform_indices(
            SHAPE_FLOOR_MARKER, 0.05 * com_props.floor_com_size, floor_com_location)
        batch = batch_for_shader(
            shader, 'LINES', {"pos": floor_com_verts})
        batch.draw(shader)

def draw_ballistics_ruler(group, com_props):
    if group.is_ballistics_preview:

        if group.frame_end > group.frame_start and group.time_of_flight > 0:
            point_positions = []

            total_frames = group.frame_end - group.frame_start

            # Get points
            p0 = Vector(group.ballistics_starting_point)
            p1 = Vector(group.reference_point)

            for frame in range(total_frames + 1):
                start_pos = (p0[0], p0[1], p0[2])
                ref_pos = (p1[0], p1[1], p1[2])
                gravity = group.gravity
                time_of_flight = float(
                    group.time_of_flight)
                elapsed_time = float(
                    frame) / group.frame_rate

                point_positions.append(projectile_position(
                    start_pos, ref_pos, gravity, time_of_flight, elapsed_time))

            # Draw lines
            for index, point_position in enumerate(
                    point_positions):
                line_batch = []
                line_color = (1.0, 0.0, 0.0, 1.0) if index + \
                    group.frame_start <= bpy.context.scene.frame_current else (0.0, 1.0, 0.0, 1.0)
                shader.uniform_float("color", line_color)
                point_coordinate = (
                    point_position[0], point_position[1], point_position[2])

                if index > 0:
                    previous_coordinate = point_positions[index - 1]
                    line_batch += [(previous_coordinate[0],
                                    previous_coordinate[1], previous_coordinate[2])]
                    line_batch += [(point_coordinate[0],
                                    point_coordinate[1], point_coordinate[2])]

                batch = batch_for_shader(
                    shader, 'LINES', {"pos": line_batch})
                batch.draw(shader)

            # Draw points
            for index, point_position in enumerate(
                    point_positions):
                shader.uniform_float(
                    "color", (0.0, 0.0, 0.0, 1.0))
                gpu.state.point_size_set(
                    com_props.ballistics_point_size)
                batch = batch_for_shader(
                    shader, 'POINTS', {"pos": point_positions})
                batch.draw(shader)

# def draw_bp(self, context):
#     com_props = bpy.context.scene.bp_com_properties
#     bp_mass_groups = bpy.context.scene.bp_mass_object_groups

#     # Go through each collection, create a batch, render it
#     if com_props.com_drawing_on and len(bp_mass_groups) > 0:
#         for group in bp_mass_groups:
#             if group.visible:
#                 if any(mass_collection is not None for mass_collection in group.mass_collections):
#                     # Get color
#                     shader.uniform_float(
#                         "color", (group.color.r, group.color.g, group.color.b, 1.0))

#                     # Draw COM Shape
#                     group_com = get_com(group)

#                     gpu.state.point_size_set(com_props.com_point_size)
#                     batch = batch_for_shader(
#                         shader, 'POINTS', {"pos": [group_com]})
#                     batch.draw(shader)

#                     # Draw Floor COM
#                     if com_props.floor_com_size > 0.0:
#                         floor_com_location = Vector(
#                             (group_com[0], group_com[1], group.com_floor_level))
#                         floor_com_verts = transform_indices(
#                             SHAPE_FLOOR_MARKER, 0.05 * com_props.floor_com_size, floor_com_location)
#                         batch = batch_for_shader(
#                             shader, 'LINES', {"pos": floor_com_verts})
#                         batch.draw(shader)

#                     # Draw Rotation Axis
#                     if group.show_axis:
#                         axis_verts = []

#                         cx = group.initial_axis.x
#                         cy = group.initial_axis.y
#                         cz = group.initial_axis.z
#                         axis_vector = numpy.array([cx, cy, cz])
#                         axis_unit = axis_vector / \
#                             numpy.linalg.norm(axis_vector)
#                         axis_verts += transform_indices([(-axis_unit[0], -axis_unit[1], -axis_unit[2]), (
#                             axis_unit[0], axis_unit[1], axis_unit[2])], 2.0, group_com)
#                         batch = batch_for_shader(
#                             shader, 'LINES', {"pos": axis_verts})
#                         batch = batch_for_shader(
#                             shader, 'LINES', {"pos": axis_verts})
#                         batch.draw(shader)

#                     # Physics Preview
#                     # Draw Reference Points
#                     if group.show_reference_point:
#                         # Reference Point
#                         gpu.state.point_size_set(
#                             com_props.reference_point_size)
#                         shader.uniform_float(
#                             "color", (group.reference_color.r, group.reference_color.g, group.reference_color.b, 1.0))
#                         batch = batch_for_shader(
#                             shader, 'POINTS', {"pos": [Vector(group.reference_point)]})
#                         batch.draw(shader)

#                         # Ballistics Starting Point
#                         shader.uniform_float(
#                             "color", (group.ballistics_starting_point_color.r, group.ballistics_starting_point_color.g, group.ballistics_starting_point_color.b, 1.0))
#                         batch = batch_for_shader(
#                             shader, 'POINTS', {"pos": [Vector(group.ballistics_starting_point)]})
#                         batch.draw(shader)

#                     # Draw ballistics curve
#                     if group.is_ballistics_preview:

#                         if group.frame_end > group.frame_start and group.time_of_flight > 0:
#                             point_positions = []

#                             total_frames = group.frame_end - group.frame_start

#                             # Get points
#                             p0 = Vector(group.ballistics_starting_point)
#                             p1 = Vector(group.reference_point)

#                             for frame in range(total_frames + 1):
#                                 start_pos = (p0[0], p0[1], p0[2])
#                                 ref_pos = (p1[0], p1[1], p1[2])
#                                 gravity = group.gravity
#                                 time_of_flight = float(
#                                     group.time_of_flight)
#                                 elapsed_time = float(
#                                     frame) / group.frame_rate

#                                 point_positions.append(projectile_position(
#                                     start_pos, ref_pos, gravity, time_of_flight, elapsed_time))

#                             # Draw lines
#                             for index, point_position in enumerate(
#                                     point_positions):
#                                 line_batch = []
#                                 line_color = (1.0, 0.0, 0.0, 1.0) if index + \
#                                     group.frame_start <= bpy.context.scene.frame_current else (0.0, 1.0, 0.0, 1.0)
#                                 shader.uniform_float("color", line_color)
#                                 point_coordinate = (
#                                     point_position[0], point_position[1], point_position[2])

#                                 if index > 0:
#                                     previous_coordinate = point_positions[index - 1]
#                                     line_batch += [(previous_coordinate[0],
#                                                     previous_coordinate[1], previous_coordinate[2])]
#                                     line_batch += [(point_coordinate[0],
#                                                     point_coordinate[1], point_coordinate[2])]

#                                 batch = batch_for_shader(
#                                     shader, 'LINES', {"pos": line_batch})
#                                 batch.draw(shader)

#                             # Draw points
#                             for index, point_position in enumerate(
#                                     point_positions):
#                                 shader.uniform_float(
#                                     "color", (0.0, 0.0, 0.0, 1.0))
#                                 gpu.state.point_size_set(
#                                     com_props.ballistics_point_size)
#                                 batch = batch_for_shader(
#                                     shader, 'POINTS', {"pos": point_positions})
#                                 batch.draw(shader)

#                     # Draw Motion Path
#                     if len(
#                             group.motion_path_points) > 0 and any(mass_collection is not None for mass_collection in group.mass_collections):
#                         point_positions = []

#                         # Get Points
#                         for path_point in group.motion_path_points:
#                             point_loc = path_point.point_location
#                             point_positions.append(
#                                 Vector((point_loc[0], point_loc[1], point_loc[2])))

#                         # Draw lines
#                         for index, point_position in enumerate(
#                                 point_positions):
#                             line_batch = []
#                             line_color = (1.0, 0.0, 0.0, 1.0) if index + \
#                                 group.frame_start <= bpy.context.scene.frame_current else (0.0, 1.0, 0.0, 1.0)
#                             shader.uniform_float("color", line_color)
#                             point_coordinate = (
#                                 point_position[0], point_position[1], point_position[2])

#                             if index > 0:
#                                 previous_coordinate = point_positions[index - 1]
#                                 line_batch += [(previous_coordinate[0],
#                                                 previous_coordinate[1], previous_coordinate[2])]
#                                 line_batch += [(point_coordinate[0],
#                                                 point_coordinate[1], point_coordinate[2])]

#                             batch = batch_for_shader(
#                                 shader, 'LINES', {"pos": line_batch})
#                             batch.draw(shader)

#                         # Draw Points
#                         for index, point_position in enumerate(
#                                 point_positions):
#                             shader.uniform_float("color", (0.0, 0.0, 0.0, 1.0))
#                             gpu.state.point_size_set(
#                                 com_props.motion_path_point_size)
#                             batch = batch_for_shader(
#                                 shader, 'POINTS', {"pos": point_positions})
#                             batch.draw(shader)
#                 else:
#                     # Physics Preview
#                     # Draw Reference Points
#                     if group.show_reference_point:
#                         # Reference Point
#                         gpu.state.point_size_set(
#                             com_props.reference_point_size)
#                         shader.uniform_float(
#                             "color", (group.reference_color.r, group.reference_color.g, group.reference_color.b, 1.0))
#                         batch = batch_for_shader(
#                             shader, 'POINTS', {"pos": [Vector(group.reference_point)]})
#                         batch.draw(shader)

#                         # Ballistics Starting Point
#                         shader.uniform_float(
#                             "color", (group.ballistics_starting_point_color.r, group.ballistics_starting_point_color.g, group.ballistics_starting_point_color.b, 1.0))
#                         batch = batch_for_shader(
#                             shader, 'POINTS', {"pos": [Vector(group.ballistics_starting_point)]})
#                         batch.draw(shader)

#                     # Draw ballistics curve
#                     if group.is_ballistics_preview:

#                         if group.frame_end > group.frame_start and group.time_of_flight > 0:
#                             point_positions = []

#                             total_frames = group.frame_end - group.frame_start

#                             # Get points
#                             p0 = Vector(group.ballistics_starting_point)
#                             p1 = Vector(group.reference_point)

#                             for frame in range(total_frames + 1):
#                                 start_pos = (p0[0], p0[1], p0[2])
#                                 ref_pos = (p1[0], p1[1], p1[2])
#                                 gravity = group.gravity
#                                 time_of_flight = float(
#                                     group.time_of_flight)
#                                 elapsed_time = float(
#                                     frame) / group.frame_rate

#                                 point_positions.append(projectile_position(
#                                     start_pos, ref_pos, gravity, time_of_flight, elapsed_time))

#                             # Draw lines
#                             for index, point_position in enumerate(
#                                     point_positions):
#                                 line_batch = []
#                                 line_color = (1.0, 0.0, 0.0, 1.0) if index + \
#                                     group.frame_start <= bpy.context.scene.frame_current else (0.0, 1.0, 0.0, 1.0)
#                                 shader.uniform_float("color", line_color)
#                                 point_coordinate = (
#                                     point_position[0], point_position[1], point_position[2])

#                                 if index > 0:
#                                     previous_coordinate = point_positions[index - 1]
#                                     line_batch += [(previous_coordinate[0],
#                                                     previous_coordinate[1], previous_coordinate[2])]
#                                     line_batch += [(point_coordinate[0],
#                                                     point_coordinate[1], point_coordinate[2])]

#                                 batch = batch_for_shader(
#                                     shader, 'LINES', {"pos": line_batch})
#                                 batch.draw(shader)

#                             # Draw points
#                             for index, point_position in enumerate(
#                                     point_positions):
#                                 shader.uniform_float(
#                                     "color", (0.0, 0.0, 0.0, 1.0))
#                                 gpu.state.point_size_set(
#                                     com_props.ballistics_point_size)
#                                 batch = batch_for_shader(
#                                     shader, 'POINTS', {"pos": point_positions})
#                                 batch.draw(shader)


def rotate_points(points, angle_deg, axis):
    import numpy

    points_np = numpy.array(points)

    angle_rad = numpy.radians(angle_deg)

    if numpy.all(axis == 0):
        return points

    axis = axis / numpy.linalg.norm(axis)

    a = numpy.cos(angle_rad)
    b = 1 - numpy.cos(angle_rad)
    c = numpy.sin(angle_rad)
    rot_mat = numpy.array([[a + axis[0]**2 * b, axis[0] * axis[1] * b - axis[2] * c, axis[0] * axis[2] * b + axis[1] * c],
                           [axis[1] * axis[0] * b + axis[2] * c, a + axis[1]
                               ** 2 * b, axis[1] * axis[2] * b - axis[0] * c],
                           [axis[2] * axis[0] * b - axis[1] * c, axis[2] * axis[1] * b + axis[0] * c, a + axis[2]**2 * b]])

    rotated_points_np = numpy.dot(points_np, rot_mat.T)

    rotated_points = [tuple(point) for point in rotated_points_np]

    return rotated_points


def transform_indices(vertices, scale, translate_vector,
                      angle_deg=0, axis=(0, 1, 0)):
    rotated_verts = rotate_points(vertices, angle_deg, axis)
    new_vertices = []
    for v in rotated_verts:
        new_vertices.append((
            (v[0] * scale) + translate_vector.x,
            (v[1] * scale) + translate_vector.y,
            (v[2] * scale) + translate_vector.z
        ))
    return new_vertices
