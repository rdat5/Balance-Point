import bpy
import gpu
import numpy
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from .utils import projectile_position, remap
from .shapes import *

shader = gpu.shader.from_builtin('UNIFORM_COLOR')

def draw_bp(self, context):
    com_props = bpy.context.scene.com_properties
    bp_mass_groups = bpy.context.scene.bp_mass_object_groups
    physics_props = bpy.context.scene.bp_physics_properties

    sel_mog = bp_mass_groups[physics_props.selected_mog] if physics_props.selected_mog else None
    com_obj = sel_mog.com_object if sel_mog else None
    # Go through each collection, create a batch, render it
    if com_props.com_drawing_on and len(bp_mass_groups) > 0:
        for group in bp_mass_groups:
            if group.visible:
                # Get color
                shader.uniform_float("color", (group.color.r, group.color.g, group.color.b, 1.0))
                # Get shape vertices
                vertex_batch = get_final_com_shape(group)
                # Draw COM Object rotation axis
                if group.show_com_object_axis and group.use_com_object and group.com_object is not None:
                    cx = group.com_object.rotation_axis_angle[1]
                    cy = group.com_object.rotation_axis_angle[2]
                    cz = group.com_object.rotation_axis_angle[3]
                    axis_vector = numpy.array([cx, cy, cz])
                    axis_unit = axis_vector / numpy.linalg.norm(axis_vector)
                    group_com_loc = Vector((group.com_location[0], group.com_location[1], group.com_location[2]))
                    vertex_batch += transform_indices([(-axis_unit[0], -axis_unit[1], -axis_unit[2]), (axis_unit[0], axis_unit[1], axis_unit[2])], group.axis_scale, group_com_loc)
                # Draw Batch
                batch = batch_for_shader(shader, 'LINES', {"pos": vertex_batch})
                batch.draw(shader)

    # Physics Preview
    # Align Preview
    if physics_props.is_align_preview:
        p1 = physics_props.align_rotation_p1
        p2 = physics_props.align_rotation_p2
        p3 = bp_mass_groups[physics_props.selected_mog].com_object.matrix_world.translation
        shader.uniform_float("color", (1.0, 1.0, 1.0, 1.0))
        vertex_batch = []
        # Points
        vertex_batch += transform_indices(POINT_MARKER, physics_props.point_scale, Vector((p1[0], p1[1], p1[2])))
        vertex_batch += transform_indices(POINT_MARKER, physics_props.point_scale, Vector((p2[0], p2[1], p2[2])))
        # Lines
        vertex_batch += [(p1[0], p1[1], p1[2]), (p2[0], p2[1], p2[2]), (p2[0], p2[1], p2[2]), (p3[0], p3[1], p3[2]), (p3[0], p3[1], p3[2]), (p1[0], p1[1], p1[2])]
        # vertex_indices = [(0, 1), (1, 2), (2, 0)]
        batch = batch_for_shader(shader, 'LINES', {"pos": vertex_batch})
        batch.draw(shader)

    # Ballistics Preview
    if physics_props.is_ballistics_preview:

        if physics_props.frame_end > physics_props.frame_start and physics_props.time_of_flight > 0:
            point_positions = []

            total_frames = physics_props.frame_end - physics_props.frame_start

            # Get points
            p1 = physics_props.ballistics_p1
            p0 = physics_props.ballistics_p0
            
            for frame in range(total_frames + 1):
                start_pos = (p0[0], p0[1], p0[2])
                ref_pos = (p1[0], p1[1], p1[2])
                gravity = physics_props.gravity
                time_of_flight = float(physics_props.time_of_flight)
                elapsed_time = float(frame) / physics_props.frame_rate

                point_positions.append(projectile_position(start_pos, ref_pos, gravity, time_of_flight, elapsed_time))
            
            # Draw lines
            for index, point_position in enumerate(point_positions):
                line_batch = []
                line_color = float(index) / float(len(point_positions))
                shader.uniform_float("color", (line_color, line_color, line_color, 1.0))
                point_coordinate = (point_position[0], point_position[1], point_position[2])

                if index > 0:
                    previous_coordinate = point_positions[index - 1]
                    line_batch += [(previous_coordinate[0], previous_coordinate[1], previous_coordinate[2])]
                    line_batch += [(point_coordinate[0], point_coordinate[1], point_coordinate[2])]
            
                gpu.state.line_width_set(2.0)
                batch = batch_for_shader(shader, 'LINES', {"pos": line_batch})
                batch.draw(shader)
            
            # Draw points
            for index, point_position in enumerate(point_positions):
                point_batch = []
                shader.uniform_float("color", (0.0, 0.0, 0.0, 1.0))
                point_batch += transform_indices(POINT_MARKER, physics_props.point_scale, point_position)

                batch = batch_for_shader(shader, 'LINES', {"pos": point_batch})
                batch.draw(shader)

            # Draw Angles

            for index, point_position in enumerate(point_positions):
                if index <= len(physics_props.calculated_mois):
                    angle_batch = [(0.0, 0.0, 1.0), (0.0, 0.0, -1.0)]

                    com_x = com_obj.rotation_axis_angle[1]
                    com_y = com_obj.rotation_axis_angle[2]
                    com_z = com_obj.rotation_axis_angle[3]

                    moi_angle = physics_props.calculated_mois[index].angle
                    angle_color = float(index) / float(len(point_positions))
                    shader.uniform_float("color", (angle_color, angle_color, angle_color, 1.0))
                    gpu.state.line_width_set(1.0)
                    batch = batch_for_shader(shader, 'LINES', {"pos": transform_indices(angle_batch, 0.2, point_position, moi_angle, (com_x, com_y, com_z))})
                    batch.draw(shader)


def get_final_com_shape(group):
    group_com_loc = Vector((group.com_location[0], group.com_location[1], group.com_location[2]))
    group_com_floor_loc = Vector((group_com_loc.x, group_com_loc.y, group.com_floor_level))
    com_shape = transform_indices(SHAPE_COM_MARKER, group.scale, group_com_loc)
    com_floor_shape = transform_indices(SHAPE_FLOOR_MARKER, group.scale, group_com_floor_loc)
    final_shape = com_shape + com_floor_shape
    if group.line_to_floor:
        final_shape += (group_com_loc.to_tuple(), group_com_floor_loc.to_tuple())
    return final_shape


def rotate_points(points, angle_deg, axis):
    # Convert list of tuples to numpy array
    points_np = numpy.array(points) 

    # Convert angle to radians
    angle_rad = numpy.radians(angle_deg)

    if numpy.all(axis == 0):
        return points

    # Normalize the rotation axis
    axis = axis / numpy.linalg.norm(axis)

    # Create the rotation matrix using Rodrigues' rotation formula
    a = numpy.cos(angle_rad)
    b = 1 - numpy.cos(angle_rad)
    c = numpy.sin(angle_rad)
    rot_mat = numpy.array([[a + axis[0]**2 * b, axis[0] * axis[1] * b - axis[2] * c, axis[0] * axis[2] * b + axis[1] * c],
                        [axis[1] * axis[0] * b + axis[2] * c, a + axis[1]**2 * b, axis[1] * axis[2] * b - axis[0] * c],
                        [axis[2] * axis[0] * b - axis[1] * c, axis[2] * axis[1] * b + axis[0] * c, a + axis[2]**2 * b]])

    # Rotate points
    rotated_points_np = numpy.dot(points_np, rot_mat.T) 

    # Convert back to list of tuples
    rotated_points = [tuple(point) for point in rotated_points_np]

    return rotated_points


def transform_indices(vertices, scale, translate_vector, angle_deg = 0, axis = (0, 1, 0)):
    rotated_verts = rotate_points(vertices, angle_deg, axis)
    new_vertices = []
    for v in rotated_verts:
        new_vertices.append((
            (v[0] * scale) + translate_vector.x,
            (v[1] * scale) + translate_vector.y,
            (v[2] * scale) + translate_vector.z
        ))
    return new_vertices