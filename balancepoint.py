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
    "version": (1, 0, 0),
    "blender": (3, 4, 0),
    "location": "View3D > Sidebar > Balance Point",
    "description": "Visualizes the center of mass of collections of objects",
    "warning": "",
    "wiki_url": "",
    "category": "3D View",
}

import bpy
import gpu
import bmesh
from mathutils import Vector
from gpu_extras.batch import batch_for_shader
from bpy.app.handlers import depsgraph_update_post
from bpy.app.handlers import frame_change_post
from bpy.app import driver_namespace

# Const

HANDLER_KEY = "BP_UPDATE_FN"

SHAPE_COM_MARKER = [
    (-1.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, -1.0, 0.0),
    (0.0, 1.0, 0.0), (0.0, 0.0, -1.0), (0.0, 0.0, 1.0)
]

SHAPE_FLOOR_MARKER = [
    (-1.0, 0.0, 0.0), (1.0, 0.0, 0.0),
    (0.0, -1.0, 0.0), (0.0, 1.0, 0.0),
    (0.5, 0.0, 0), (0.4619, 0.1913, 0),
    (0.4619, 0.1913, 0), (0.3536, 0.3536, 0), 
    (0.3536, 0.3536, 0), (0.1913, 0.4619, 0), 
    (0.1913, 0.4619, 0), (0.0, 0.5, 0), 
    (0.0, 0.5, 0), (-0.1913, 0.4619, 0), 
    (-0.1913, 0.4619, 0), (-0.3536, 0.3536, 0), 
    (-0.3536, 0.3536, 0), (-0.4619, 0.1913, 0), 
    (-0.4619, 0.1913, 0), (-0.5, 0.0, 0), 
    (-0.5, 0.0, 0), (-0.4619, -0.1913, 0), 
    (-0.4619, -0.1913, 0), (-0.3536, -0.3536, 0), 
    (-0.3536, -0.3536, 0), (-0.1913, -0.4619, 0), 
    (-0.1913, -0.4619, 0), (-0.0, -0.5, 0), 
    (-0.0, -0.5, 0), (0.1913, -0.4619, 0), 
    (0.1913, -0.4619, 0), (0.3536, -0.3536, 0), 
    (0.3536, -0.3536, 0), (0.4619, -0.1913, 0),
    (0.4619, -0.1913, 0), (0.5, 0.0, 0)]

# Shader setup

shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')

# Classes

## Properties

class MassObjectGroup(bpy.types.PropertyGroup):
    visible : bpy.props.BoolProperty(name="Visible", default=True)
    mass_object_collection : bpy.props.PointerProperty(name="Mass Object Collection", type=bpy.types.Collection)
    com_floor_level : bpy.props.FloatProperty(name="Floor Level", default=0.0)
    line_to_floor : bpy.props.BoolProperty(name="Draw Line to Floor", default=False)
    com_location : bpy.props.FloatVectorProperty(name="Location of Center of Mass")
    color : bpy.props.FloatVectorProperty(name="CoM Marker Color", description="Color of the CoM Marker", default=(1, 0, 1), subtype='COLOR', min=0.0, max=1.0)
    scale : bpy.props.FloatProperty(name="CoM Marker Scale", default=0.05, description="Size of the CoM Markers (in meters)", min=0)

class ComProperties(bpy.types.PropertyGroup):
    com_tracking_on : bpy.props.BoolProperty(name="CoM Tracking Enabled", default=True)

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
        bp_mass_groups = context.scene.bp_mass_object_groups

        # Com Tracking On/Off
        row = layout.row(align=True)
        row.prop(com_props, "com_tracking_on")
        # Mass Object Groups
        row = layout.row(align=True)
        row.label(text="Mass Object Groups:")
        box = layout.box()
        for mass_group in bp_mass_groups:
            innerBox = box.box()
            row = innerBox.row(align=True)
            row.label(text="Mass Object Collection")
            row.prop(mass_group, "visible")
            row = innerBox.row(align=True)
            row.prop(mass_group, "mass_object_collection", text="")
            row.prop(mass_group, "color", text="")
            row = innerBox.row(align=True)
            row.prop(mass_group, "scale")
            row = innerBox.row(align=True)
            row.prop(mass_group, "line_to_floor")
            row.prop(mass_group, "com_floor_level")
            if mass_group.mass_object_collection is not None and com_props.com_tracking_on:
                cl = mass_group.com_location
                row = innerBox.row(align=True)
                cl = mass_group.com_location
                row.label(text="CoM Loc: (%.2f, %.2f, %.2f)" % (cl[0], cl[1], cl[2]))

        row = box.row()
        add_bp_group_text = 'Add' if len(bp_mass_groups) > 1 else 'Add Mass Object Group'
        row.operator("balance_point.massgroup_add", text=add_bp_group_text, icon="ADD")
        if len(bp_mass_groups) > 1:
            row.operator("balance_point.massgroup_remove", text="Remove", icon="REMOVE")

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

class AddMassObjectGroup(bpy.types.Operator):
    """Adds a new Mass Object Group"""
    bl_idname = "balance_point.massgroup_add"
    bl_label = "Add new Mass Object Group"

    def execute(self, context):
        bpy.context.scene.bp_mass_object_groups.add()
        return {'FINISHED'}

class RemoveMassObjectGroup(bpy.types.Operator):
    """Adds a new Mass Object Group"""
    bl_idname = "balance_point.massgroup_remove"
    bl_label = "Remove last Mass Object Group"

    def execute(self, context):
        if len(bpy.context.scene.bp_mass_object_groups) > 1:
            bpy.context.scene.bp_mass_object_groups.remove(len(bpy.context.scene.bp_mass_object_groups) - 1)
        return {'FINISHED'}

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
            ToggleCOMUpdate._handle = bpy.types.SpaceView3D.draw_handler_add(draw_bp, (None, None), 'WINDOW', 'POST_VIEW')
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

def transform_indices(vertices, scale, translate_vector):
    new_vertices = []
    for v in vertices:
        new_vertices.append((
            (v[0] * scale) + translate_vector.x,
            (v[1] * scale) + translate_vector.y,
            (v[2] * scale) + translate_vector.z
            ))
    return new_vertices

def get_final_com_shape(group):
    group_com_loc = Vector((group.com_location[0], group.com_location[1], group.com_location[2]))
    group_com_floor_loc = Vector((group_com_loc.x, group_com_loc.y, group.com_floor_level))
    com_shape = transform_indices(SHAPE_COM_MARKER, group.scale, group_com_loc)
    com_floor_shape = transform_indices(SHAPE_FLOOR_MARKER, group.scale, group_com_floor_loc)
    final_shape = com_shape + com_floor_shape
    if group.line_to_floor:
        final_shape += (group_com_loc.to_tuple(), group_com_floor_loc.to_tuple())
    return final_shape

def draw_bp(self, context):
    com_props = bpy.context.scene.com_properties
    bp_mass_groups = bpy.context.scene.bp_mass_object_groups

    # Go through each collection, create a batch, render it
    for group in bp_mass_groups:
        if group.visible:
            # Get color
            shader.uniform_float("color", (group.color.r, group.color.g, group.color.b, 1.0))
            # Get shape vertices
            batch = batch_for_shader(shader, 'LINES', {"pos": get_final_com_shape(group)})
            batch.draw(shader)

def get_total_mass(objects):
    total_mass = 0

    for obj in objects:
        if obj.get("active"):
            obj_mass = obj.get("density") * obj.get("volume")

            total_mass += obj_mass
    
    return total_mass

def initialize_bp_mass_groups():
    bpy.context.scene.bp_mass_object_groups.clear()
    bpy.context.scene.bp_mass_object_groups.add()

def update_mass_group_com(scene):
    com_props = bpy.context.scene.com_properties
    bp_mass_groups = bpy.context.scene.bp_mass_object_groups

    if com_props.com_tracking_on:
        for mass_group in bp_mass_groups:
            if mass_group.mass_object_collection is not None:
                mgc = get_com(mass_group.mass_object_collection)
                mass_group.com_location = [mgc.x, mgc.y, mgc.z]

# Class Registration

classes = (
    MassObjectGroup,
    ComProperties,
    CenterOfMassPanel,
    MassPropertiesPanel,
    AddMassObjectGroup,
    RemoveMassObjectGroup,
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
    bpy.types.Scene.bp_mass_object_groups = bpy.props.CollectionProperty(type=MassObjectGroup)
    bpy.app.timers.register(initialize_bp_mass_groups, first_interval=0.1)

    # Add depsgraph, frame_change handler callbacks
    if HANDLER_KEY not in driver_namespace:
        depsgraph_update_post.append(update_mass_group_com)
        frame_change_post.append(update_mass_group_com)
        driver_namespace[HANDLER_KEY] = update_mass_group_com

def unregister():
    if ToggleCOMUpdate._handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(ToggleCOMUpdate._handle, 'WINDOW')

    for cls in classes:
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.com_properties
    del bpy.types.Scene.bp_mass_object_groups

    # Remove depsgraph, frame_change handler callbacks
    if HANDLER_KEY in driver_namespace:
        if driver_namespace[HANDLER_KEY] in depsgraph_update_post:
            depsgraph_update_post.remove(driver_namespace[HANDLER_KEY])
            frame_change_post.remove(driver_namespace[HANDLER_KEY])

if __name__ == "__main__":
    register()