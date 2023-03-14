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
    "version": (0, 8, 0),
    "blender": (3, 4, 0),
    "location": "View3D > Tools > Balance Point",
    "description": "Visualizes the center of mass of a collection of objects",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}

handler_key = "BP_UPDATE_FN"

import bpy
import bmesh
import mathutils
from bpy.app.handlers import depsgraph_update_post
from bpy.app.handlers import frame_change_post
from bpy.app import driver_namespace

# Classes

## Properties

def update_floor(self, context):
    set_com_obj(context.scene)

class ComProperties(bpy.types.PropertyGroup):
    com_collection : bpy.props.PointerProperty(name="Mass Object Collection", type=bpy.types.Collection)
    com_object : bpy.props.PointerProperty(name="Center of Mass Object", type=bpy.types.Object)
    com_floor_object : bpy.props.PointerProperty(name="Center of Mass Object (floor)", type=bpy.types.Object)
    com_floor_level : bpy.props.FloatProperty(name="Floor Level", default=0.0, description="The point where gravity pushes the center of mass towards", update=update_floor)

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

        # Basic Setup
        row = layout.row()
        row.operator("object.bp_basic_add", icon='PRESET_NEW')

        # Center of Mass
        row = layout.row(heading="Center of Mass Object", align=True)
        row.prop(com_props, "com_object", text="")
        row = layout.row(heading="Floor Center of Mass Object", align=True)
        row.prop(com_props, "com_floor_object", text="")
        row = layout.row(heading="Floor Level", align=True)
        row.prop(com_props, "com_floor_level", text="")

        # Collection
        row = layout.row(heading="Mass Object Collection", align=True)
        row.prop(com_props, "com_collection", text="")

        # Update
        handler_fn_is_on = (handler_key in driver_namespace and driver_namespace[handler_key] in depsgraph_update_post)
        update_icon = 'PAUSE' if handler_fn_is_on else 'PLAY'
        update_text = 'Update Off' if handler_fn_is_on else 'Update On'

        row = layout.row(heading="Update Center of Mass Location")
        row.scale_y = 2.0
        row.operator("object.toggle_com_update", text=update_text, icon=update_icon)

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
        row.operator("object.comprop_add", text="Add", icon='ADD')
        row.operator("object.comprop_del", text="Remove", icon='REMOVE')
        
        # Volume
        col = layout.column(align=True)
        
        row = col.row()
        row.label(text="Volume")
        
        row = col.row()
        row.operator("object.calculate_volume", icon='CUBE')
        
        # Object Origin to Center of Mass
        col = layout.column(align=True)

        row = col.row()
        row.label(text="Set Selected CoM to Origins")

        row = col.row()
        row.operator("object.origin_set", text='Origin to Center of Mass (Volume)', icon='DOT').type='ORIGIN_CENTER_OF_VOLUME'

        # Set active to selected
        col = layout.column(align=True)
        
        row = col.row()
        row.label(text="Set active to selected")
        
        row = col.row(align=True)
        row.operator("object.active_true", icon='RADIOBUT_ON')
        row.operator("object.active_false", icon='RADIOBUT_OFF')
        col.operator("object.toggle_active", icon='ARROW_LEFTRIGHT')
        
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

class AddBasicCOMSetup(bpy.types.Operator):
    """Add basic setup for using Balance Point"""
    bl_idname = "object.bp_basic_add"
    bl_label = "Add Basic Balance Point Setup"

    def execute(self, context):
        com_props = context.scene.com_properties

        # Create Collections

        balance_point_col = bpy.data.collections.new(name="Balance Point")
        context.collection.children.link(balance_point_col)

        mass_obj_col = bpy.data.collections.new(name="BP Mass Objects")
        center_of_mass_obj_col = bpy.data.collections.new(name="BP COM Markers")
        balance_point_col.children.link(mass_obj_col)
        balance_point_col.children.link(center_of_mass_obj_col)

        # Create Objects
        main_com_marker = bpy.data.objects.new("CoM Main", None)
        floor_com_marker = bpy.data.objects.new("CoM Floor", None)

        main_com_marker.empty_display_size = 1.0
        floor_com_marker.empty_display_size = .5

        main_com_marker.empty_display_type = 'PLAIN_AXES'
        floor_com_marker.empty_display_type = 'PLAIN_AXES'

        main_com_marker.show_in_front = True
        floor_com_marker.show_in_front = True

        main_com_marker.hide_select = True
        floor_com_marker.hide_select = True

        example_mesh = bpy.data.meshes.new('Basic_Cube')
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bm.to_mesh(example_mesh)
        bm.free()
        example_mass_obj = bpy.data.objects.new("Example Mass", example_mesh)

        example_mass_obj["active"] = True
        example_mass_obj["density"] = 1.0
        example_mass_obj["volume"] = 1.0

        # Link to Scene in Appropriate Collections
        center_of_mass_obj_col.objects.link(main_com_marker)
        center_of_mass_obj_col.objects.link(floor_com_marker)
        mass_obj_col.objects.link(example_mass_obj)

        # Add To BP if available
        if com_props.com_object is None:
            com_props.com_object = main_com_marker
        if com_props.com_floor_object is None:
            com_props.com_floor_object = floor_com_marker
        if com_props.com_collection is None:
            com_props.com_collection = mass_obj_col

        return {'FINISHED'}

class AddMassProps(bpy.types.Operator):
    """Add mass properties to selected objects"""
    bl_idname = "object.comprop_add"
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
    bl_idname = "object.comprop_del"
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
    bl_idname = "object.toggle_active"
    bl_label = "Toggle Active"
    
    def execute(self, context):
        selObj = context.selected_objects
        
        for obj in selObj:
            if obj.get('active') is not None:
                set_active(obj, (not obj['active']))
        return {'FINISHED'} 

class SetActiveTrue(bpy.types.Operator):
    """Toggles the active property"""
    bl_idname = "object.active_true"
    bl_label = "Active"
    
    def execute(self, context):
        selObj = context.selected_objects
        
        for obj in selObj:
            if obj.get('active') is not None:
                set_active(obj, True)
        return {'FINISHED'} 

class SetActiveFalse(bpy.types.Operator):
    """Toggles the active property"""
    bl_idname = "object.active_false"
    bl_label = "Inactive"
    
    def execute(self, context):
        selObj = context.selected_objects
        
        for obj in selObj:
            if obj.get('active') is not None:
                set_active(obj, False)
        return {'FINISHED'} 

class CalculateVolume(bpy.types.Operator):
    """Calculate volume of selected"""
    bl_idname = "object.calculate_volume"
    bl_label = "Calculate volume of selected"
    
    def execute(self, context):
        selObj = context.selected_objects
        
        for obj in selObj:
            if obj.get('volume') is not None and obj.type == 'MESH':
                obj['volume'] = get_volume(obj)
        return {'FINISHED'} 

class ToggleCOMUpdate(bpy.types.Operator):
    """Adds/Removes center of mass update function from depsgraph update handler"""
    bl_idname = "object.toggle_com_update"
    bl_label = "Toggle COM Update"

    def execute(self, context):
        if handler_key in driver_namespace:
            if driver_namespace[handler_key] in depsgraph_update_post:
                depsgraph_update_post.remove(driver_namespace[handler_key])
                frame_change_post.remove(driver_namespace[handler_key])

                del driver_namespace[handler_key]
        else:
            depsgraph_update_post.append(set_com_obj)
            frame_change_post.append(set_com_obj)
            driver_namespace[handler_key] = set_com_obj

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
    center_of_mass = mathutils.Vector((0, 0, 0))

    total_mass = 0
    weighted_sum = mathutils.Vector((0, 0, 0))

    for obj in coll.all_objects:
        if obj.get("active"):
            obj_mass = obj.get("density") * obj.get("volume")

            total_mass += obj_mass
            weighted_sum += (obj_mass * obj.matrix_world.translation)
    
    if total_mass > 0:
        center_of_mass = weighted_sum / total_mass

    return center_of_mass

def set_com_obj(scene):
    context = bpy.context

    com_obj = context.scene.com_properties.get("com_object")
    com_floor_obj = context.scene.com_properties.get("com_floor_object")
    com_floor_lvl = context.scene.com_properties.get("com_floor_level")
    com_col = context.scene.com_properties.get("com_collection")

    # Have to initialize properties
    if com_floor_lvl is None:
        com_floor_lvl = 0.0

    if (com_obj is not None and com_col is not None):
        com_obj.matrix_world.translation = get_com(com_col)
        if (com_floor_obj is not None):
            com_loc = com_obj.matrix_world.translation
            com_floor_obj.matrix_world.translation = mathutils.Vector((com_loc.x, com_loc.y, com_floor_lvl))

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
    AddBasicCOMSetup,
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

    if handler_key in driver_namespace:
        if driver_namespace[handler_key] in depsgraph_update_post:
            depsgraph_update_post.remove(driver_namespace[handler_key])
            frame_change_post.remove(driver_namespace[handler_key])

            del driver_namespace[handler_key]

if __name__ == "__main__":
    register()