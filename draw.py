import bpy
import gpu
import numpy
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

from .shapes import *

shader = gpu.shader.from_builtin('UNIFORM_COLOR')

def draw_bp(self, context):
    com_props = bpy.context.scene.com_properties
    bp_mass_groups = bpy.context.scene.bp_mass_object_groups
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