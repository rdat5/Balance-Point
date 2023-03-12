bl_info = {
    "name": "Balance Point",
    "author": "Ray Allen Datuin",
    "version": (0, 0, 1),
    "blender": (3, 4, 0),
    "location": "View3D > Tools > Balance Point",
    "description": "Visualizes the center of mass of a collection of objects",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}

import bpy
import bmesh

# Classes

## Panels

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

## Operators

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

# Class Registration

classes = (
    MassPropertiesPanel,
    AddMassProps,
    RemoveMassProps,
    ToggleActiveProperty,
    SetActiveTrue,
    SetActiveFalse,
    CalculateVolume
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()