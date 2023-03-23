import bpy

class MassObjectGroup(bpy.types.PropertyGroup):
    visible: bpy.props.BoolProperty(name="Visible", default=True)
    mass_object_collection: bpy.props.PointerProperty(name="Mass Object Collection", type=bpy.types.Collection)
    com_floor_level: bpy.props.FloatProperty(name="Floor Level", default=0.0)
    line_to_floor: bpy.props.BoolProperty(name="Draw Line to Floor", default=False)
    com_location: bpy.props.FloatVectorProperty(name="Location of Center of Mass")
    color: bpy.props.FloatVectorProperty(name="CoM Marker Color", description="Color of the CoM Marker", default=(
        1, 0, 1), subtype='COLOR', min=0.0, max=1.0)
    scale: bpy.props.FloatProperty(name="CoM Marker Scale", default=0.05,
                                   description="Size of the CoM Markers (in meters)", min=0)


class ComProperties(bpy.types.PropertyGroup):
    com_tracking_on: bpy.props.BoolProperty(name="CoM Tracking Enabled", default=True)
    com_drawing_on: bpy.props.BoolProperty(name="CoM Drawing Enabled", default=False)