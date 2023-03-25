import bpy
import bmesh

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

    @classmethod
    def poll(cls, context):
        obj = context.object

        return obj.type == 'MESH' and obj.get('active') is None

    def execute(self, context):
        sel_obj = context.selected_objects

        for obj in sel_obj:
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

    @classmethod
    def poll(cls, context):
        obj = context.object

        return obj.type == 'MESH' and obj.get('active') is not None

    def execute(self, context):
        sel_obj = context.selected_objects

        for obj in sel_obj:
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

    @classmethod
    def poll(cls, context):
        obj = context.object

        return obj.type == 'MESH' and obj.get('active') is not None

    def execute(self, context):
        sel_obj = context.selected_objects

        for obj in sel_obj:
            if obj.get('active') is not None:
                set_active(obj, (not obj['active']))
        return {'FINISHED'}


class SetActiveTrue(bpy.types.Operator):
    """Toggles the active property"""
    bl_idname = "balance_point.set_active_true"
    bl_label = "Active"

    @classmethod
    def poll(cls, context):
        obj = context.object

        return obj.type == 'MESH' and obj.get('active') is not None

    def execute(self, context):
        sel_obj = context.selected_objects

        for obj in sel_obj:
            if obj.get('active') is not None:
                set_active(obj, True)
        return {'FINISHED'}


class SetActiveFalse(bpy.types.Operator):
    """Toggles the active property"""
    bl_idname = "balance_point.set_active_false"
    bl_label = "Inactive"

    @classmethod
    def poll(cls, context):
        obj = context.object

        return obj.type == 'MESH' and obj.get('active') is not None

    def execute(self, context):
        sel_obj = context.selected_objects

        for obj in sel_obj:
            if obj.get('active') is not None:
                set_active(obj, False)
        return {'FINISHED'}


class CalculateVolume(bpy.types.Operator):
    """Calculate volume of selected"""
    bl_idname = "balance_point.calculate_volume"
    bl_label = "Calculate volume of selected"

    @classmethod
    def poll(cls, context):
        obj = context.object

        return obj.type == 'MESH' and obj.get('volume') is not None

    def execute(self, context):
        sel_obj = context.selected_objects

        for obj in sel_obj:
            if obj.get('volume') is not None and obj.type == 'MESH':
                obj['volume'] = get_volume(obj) * 1000
        return {'FINISHED'}


class SetDensity(bpy.types.Operator):
    """Set the density of selected objects"""
    bl_idname = "balance_point.set_density"
    bl_label = "Set density of selected"

    @classmethod
    def poll(cls, context):
        obj = context.object

        return obj.type == 'MESH' and obj.get('density') is not None

    def execute(self, context):
        sel_obj = context.selected_objects
        com_props = context.scene.com_properties
        
        for obj in sel_obj:
            if obj.get('density') is not None:
                obj['density'] = com_props.mass_density_set
        return {'FINISHED'}


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