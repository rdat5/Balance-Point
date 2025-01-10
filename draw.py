import bpy
import gpu
import numpy
from gpu_extras.batch import batch_for_shader
from mathutils import Vector
from .utils import projectile_position
from .shapes import *

shader = gpu.shader.from_builtin('UNIFORM_COLOR')

def draw_bp(self, context):
    com_props = bpy.context.scene.com_properties
    bp_mass_groups = bpy.context.scene.bp_mass_object_groups
    physics_props = bpy.context.scene.bp_physics_properties
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
        shader.uniform_float("color", (1.0, 1.0, 1.0, 1.0))
        
        vertex_batch = []
        # Points
        p1 = physics_props.ballistics_p1
        p0 = physics_props.ballistics_p0
        vertex_batch += transform_indices(POINT_MARKER, physics_props.point_scale * 2, Vector((p1[0], p1[1], p1[2])))

        if physics_props.frame_end > physics_props.frame_start:
            total_frames = physics_props.frame_end - physics_props.frame_start
            last_point = (p0[0], p0[1], p0[2])
            for frame in range(1, total_frames + 1):
                start_pos = (p0[0], p0[1], p0[2])
                ref_pos = (p1[0], p1[1], p1[2])
                gravity = physics_props.gravity
                time_of_flight = float(physics_props.time_of_flight)
                elapsed_time = float(frame) / physics_props.frame_rate

                point_position = projectile_position(start_pos, ref_pos, gravity, time_of_flight, elapsed_time)
                vertex_batch += transform_indices(POINT_MARKER, physics_props.point_scale, point_position)

                # Lines
                vertex_batch += [last_point, point_position]
                last_point = point_position
                pass

        batch = batch_for_shader(shader, 'LINES', {"pos": vertex_batch})
        batch.draw(shader)
        pass


def get_final_com_shape(group):
    group_com_loc = Vector((group.com_location[0], group.com_location[1], group.com_location[2]))
    group_com_floor_loc = Vector((group_com_loc.x, group_com_loc.y, group.com_floor_level))
    com_shape = transform_indices(SHAPE_COM_MARKER, group.scale, group_com_loc)
    com_floor_shape = transform_indices(SHAPE_FLOOR_MARKER, group.scale, group_com_floor_loc)
    final_shape = com_shape + com_floor_shape
    if group.line_to_floor:
        final_shape += (group_com_loc.to_tuple(), group_com_floor_loc.to_tuple())
    return final_shape


def transform_indices(vertices, scale, translate_vector):
    new_vertices = []
    for v in vertices:
        new_vertices.append((
            (v[0] * scale) + translate_vector.x,
            (v[1] * scale) + translate_vector.y,
            (v[2] * scale) + translate_vector.z
        ))
    return new_vertices