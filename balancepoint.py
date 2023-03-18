# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Balance Point",
    "author": "Ray Allen Datuin",
    "version": (0, 9, 0),
    "blender": (3, 4, 0),
    "location": "View3D > Tools > Balance Point",
    "description": "Visualizes the center of mass of a collection of objects",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}

import bpy
import bgl
import gpu
import bmesh
from mathutils import Vector
from gpu_extras.batch import batch_for_shader

# Const

SHAPE_COM_MARKER = [
    Vector((-1.0, 0.0, 0.0)),
    Vector((1.0, 0.0, 0.0)),
    Vector((0.0, -1.0, 0.0)),
    Vector((0.0, 1.0, 0.0)),
    Vector((0.0, 0.0, -1.0)),
    Vector((0.0, 0.0, 1.0))
]

SHAPE_FLOOR_MARKER = [
    Vector((-1.0, 0.0, 0.0)),
    Vector((1.0, 0.0, 0.0)),
    Vector((0.0, -1.0, 0.0)),
    Vector((0.0, 1.0, 0.0)),
    Vector((0.0, 0.5, 0.0)),
    Vector((0.353553, 0.353553, 0.0)),
    Vector((0.353553, 0.353553, 0.0)),
    Vector((0.5, 0.0, 0.0)),
    Vector((0.5, 0.0, 0.0)),
    Vector((0.353553, -0.353553, 0.0)),
    Vector((0.353553, -0.353553, 0.0)),
    Vector((0.0, -0.5, 0.0)),
    Vector((0.0, -0.5, 0.0)),
    Vector((-0.353553, -0.353553, 0.0)),
    Vector((-0.353553, -0.353553, 0.0)),
    Vector((-0.5, 0.0, 0.0)),
    Vector((-0.5, 0.0, 0.0)),
    Vector((-0.353553, 0.353553, 0.0)),
    Vector((-0.353553, 0.353553, 0.0)),
    Vector((0.0, 0.5, 0.0)),
]

# Classes

## Properties

class ComProperties(bpy.types.PropertyGroup):
    com_collection : bpy.props.PointerProperty(name="Mass Object Collection", type=bpy.types.Collection)
    com_floor_level : bpy.props.FloatProperty(name="Floor Level", default=0.0)
    com_scale : bpy.props.FloatProperty(name="CoM Marker Scale", default=0.05, description="Size of the CoM Markers (in meters)", min=0)
    com_color : bpy.props.FloatVectorProperty(name="CoM Marker Color", description="Color of the CoM Marker", default=(1, 0, 1), subtype='COLOR', min=0.0, max=1.0)
    com_thickness : bpy.props.IntProperty(name="Com Marker Pixel Width", default=2, description="Thickness of CoM Marker", min=1, max=10)

## Panels

class CenterOfMassPanel(bpy.types.Panel):
    """Center of mass settings"""
    bl_label = "Center of Mass Settings"
    bl_idname = "OBJECT_PT_center_of_mass_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Balance Point"

    def draw(self, context):
        layout = self.layout
        com_props = context.scene.com_properties

        # Collection
        row = layout.row(heading="Mass Object Collection", align=True)
        row.prop(com_props, "com_collection", text="")

        # Floor Level
        row = layout.row(heading="Floor Level", align=True)
        row.prop(com_props, "com_floor_level", text="")

        # CoM Scale
        row = layout.row(align=True)
        row.prop(com_props, "com_scale")
        row = layout.row(align=True)
        row.prop(com_props, "com_thickness")

        # CoM Color
        row = layout.row(align=True)
        row.prop(com_props, "com_color")

        # Update
        handler_fn_is_on = (ToggleCOMUpdate._handle is not None)
        update_icon = 'PAUSE' if handler_fn_is_on else 'PLAY'
        update_text = 'Update Off' if handler_fn_is_on else 'Update On'

        row = layout.row(heading="Update Center of Mass Location")
        row.scale_y = 2.0
        row.operator("balance_point.toggle_com_update", text=update_text, icon=update_icon)

class MassPropertiesPanel(bpy.types.Panel):
    """Mass properties panel"""
    bl_label = "Mass Properties"
    bl_idname = "OBJECT_PT_mass_properties_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Balance Point"
    
    def draw(self, context):
        layout = self.layout
        selObj = context.selected_objects
        
        # Mass properties
        col = layout.column(align=True)
        
        row = col.row()
        row.label(text="Mass properties to selected")

        row = col.row(align=True)
        row.operator("balance_point.massprop_add", text="Add", icon='ADD')
        row.operator("balance_point.massprop_del", text="Remove", icon='REMOVE')
        
        # Volume
        col = layout.column(align=True)
        
        row = col.row()
        row.label(text="Volume")
        
        row = col.row()
        row.operator("balance_point.calculate_volume", icon='CUBE')
        
        # Object Origin to Center of Mass
        col = layout.column(align=True)

        row = col.row()
        row.label(text="Set Selected Origin(s) to Object CoM")

        row = col.row()
        row.operator("object.origin_set", text='Origin to Center of Mass (Volume)', icon='DOT').type='ORIGIN_CENTER_OF_VOLUME'

        # Set active to selected
        col = layout.column(align=True)
        
        row = col.row()
        row.label(text="Set active to selected")
        
        row = col.row(align=True)
        row.operator("balance_point.set_active_true", icon='RADIOBUT_ON')
        row.operator("balance_point.set_active_false", icon='RADIOBUT_OFF')
        col.operator("balance_point.toggle_active", icon='ARROW_LEFTRIGHT')
        
        # Selected mass objects
        col = layout.column(align=True)
        
        row = col.row(align=True)
        row.label(text="Selected Mass Objects: ")
        for obj in selObj:
            if obj.get('volume') is not None:
                box = col.box()
                
                # split box
                split = box.split(factor=0.4)
                
                # left column
                col1 = split.column(align=True)
                col1.label(text="" + obj.name)
                
                # get if active
                if obj.get("active") == True:
                    col1.label(text="Active", icon='RADIOBUT_ON')
                elif obj.get("active") == False:
                    col1.label(text="Inactive", icon='RADIOBUT_OFF')
                
                # right column
                obj_mass = round(obj.get("density") * obj.get("volume") * obj.get("active"), 3)
                
                col2 = split.column(align=True)
                col2.prop(obj, '["density"]')
                col2.prop(obj, '["volume"]')
                col2.label(text="Mass: "  + str(obj_mass))
        if len(selObj) > 0:
            row = layout.row()
            row.label(text="Total Mass of Selected: " + str(round(get_total_mass(selObj), 3)))

## Operators

class AddMassProps(bpy.types.Operator):
    """Add mass properties to selected objects"""
    bl_idname = "balance_point.massprop_add"
    bl_label = "Add mass properties to selected"
    
    def execute(self, context):
        selObj = context.selected_objects
        
        for obj in selObj:
            if obj.type == 'MESH':
                if obj.get('active') is None:
                    obj["active"] = True
                if obj.get('density') is None:
                    obj["density"] = 1.0
                if obj.get('volume') is None:
                    obj["volume"] = 1.0
        return {'FINISHED'} 

class RemoveMassProps(bpy.types.Operator):
    """Remove mass properties from selected objects"""
    bl_idname = "balance_point.massprop_del"
    bl_label = "Remove mass properties from selected"
    
    def execute(self, context):
        selObj = context.selected_objects
        
        for obj in selObj:
            if obj.type == 'MESH':
                if obj.get('active') is not None:
                    del obj["active"]
                if obj.get('density') is not None:
                    del obj["density"]
                if obj.get('volume') is not None:
                    del obj["volume"]
        return {'FINISHED'} 

class ToggleActiveProperty(bpy.types.Operator):
    """Toggles the active property"""
    bl_idname = "balance_point.toggle_active"
    bl_label = "Toggle Active"
    
    def execute(self, context):
        selObj = context.selected_objects
        
        for obj in selObj:
            if obj.get('active') is not None:
                set_active(obj, (not obj['active']))
        return {'FINISHED'} 

class SetActiveTrue(bpy.types.Operator):
    """Toggles the active property"""
    bl_idname = "balance_point.set_active_true"
    bl_label = "Active"
    
    def execute(self, context):
        selObj = context.selected_objects
        
        for obj in selObj:
            if obj.get('active') is not None:
                set_active(obj, True)
        return {'FINISHED'} 

class SetActiveFalse(bpy.types.Operator):
    """Toggles the active property"""
    bl_idname = "balance_point.set_active_false"
    bl_label = "Inactive"
    
    def execute(self, context):
        selObj = context.selected_objects
        
        for obj in selObj:
            if obj.get('active') is not None:
                set_active(obj, False)
        return {'FINISHED'} 

class CalculateVolume(bpy.types.Operator):
    """Calculate volume of selected"""
    bl_idname = "balance_point.calculate_volume"
    bl_label = "Calculate volume of selected"
    
    def execute(self, context):
        selObj = context.selected_objects
        
        for obj in selObj:
            if obj.get('volume') is not None and obj.type == 'MESH':
                obj['volume'] = get_volume(obj)
        return {'FINISHED'} 

class ToggleCOMUpdate(bpy.types.Operator):
    """Adds/Removes center of mass render function from draw handler"""
    bl_idname = "balance_point.toggle_com_update"
    bl_label = "Toggle COM Update"

    _handle = None

    def execute(self, context):
        if ToggleCOMUpdate._handle is None:
            # add the draw handler
            ToggleCOMUpdate._handle = bpy.types.SpaceView3D.draw_handler_add(render_com, (None, None), 'WINDOW', 'POST_VIEW')
        else:
            # remove draw handler
            bpy.types.SpaceView3D.draw_handler_remove(ToggleCOMUpdate._handle, 'WINDOW')
            ToggleCOMUpdate._handle = None

        # Force re render of viewport
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
        return {'FINISHED'}

# Function Definitions

def set_active(obj, act):
    obj['active'] = act
    if act == True:
        obj.display_type = 'SOLID'
    elif act == False:
        obj.display_type = 'WIRE'

def get_volume(obj):
    volume = 0.0
    
    depsgraph = bpy.context.evaluated_depsgraph_get()
    obj_eval = obj.evaluated_get(depsgraph)
    me = obj_eval.to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    obj_eval.to_mesh_clear()
    volume = bm.calc_volume()
    bm.free()
    
    return volume

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

def add_vector_to_array(vectors, add_vector):
    new_vectors = []
    for vector in vectors:
        new_vector = vector + add_vector
        new_vectors.append(new_vector)
    return new_vectors

def multiply_vectors_by_scalar(vectors, scalar):
    result = []
    for vector in vectors:
        result.append(vector * scalar)
    return result

def render_com(self, context):
    com_props = bpy.context.scene.com_properties

    com_pos = (Vector((0, 0, 0)))

    if com_props.com_collection is not None:
        com_pos = (get_com(com_props.com_collection))

    marker_color = (com_props.com_color.r, com_props.com_color.g, com_props.com_color.b, 0.0)

    # Get shapes
    new_com_shape = multiply_vectors_by_scalar(SHAPE_COM_MARKER, com_props.com_scale)
    new_floor_com_shape = multiply_vectors_by_scalar(SHAPE_FLOOR_MARKER, com_props.com_scale)
    translated_com_shape = add_vector_to_array(new_com_shape, com_pos)
    translated_floor_com_shape = add_vector_to_array(new_floor_com_shape, Vector((com_pos.x, com_pos.y, com_props.com_floor_level)))

    # Render
    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    batch = batch_for_shader(shader, 'LINES', {"pos": translated_com_shape + translated_floor_com_shape})

    shader.uniform_float("color", marker_color)
    bgl.glLineWidth(com_props.com_thickness)
    gpu.state.active_shader = shader
    batch.draw(shader)

def get_total_mass(objects):
    total_mass = 0

    for obj in objects:
        if obj.get("active"):
            obj_mass = obj.get("density") * obj.get("volume")

            total_mass += obj_mass
    
    return total_mass

# Class Registration

classes = (
    ComProperties,
    CenterOfMassPanel,
    MassPropertiesPanel,
    AddMassProps,
    RemoveMassProps,
    ToggleActiveProperty,
    SetActiveTrue,
    SetActiveFalse,
    CalculateVolume,
    ToggleCOMUpdate
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.com_properties = bpy.props.PointerProperty(type=ComProperties)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.com_properties

    bpy.types.SpaceView3D.draw_handler_remove(ToggleCOMUpdate._handle, 'WINDOW')

if __name__ == "__main__":
    register()