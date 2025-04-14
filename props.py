import bpy


class CalculatedMOI(bpy.types.PropertyGroup):
    moment_of_inertia: bpy.props.FloatProperty(
        name="Set Density", default=1.0, soft_min=0)
    angle: bpy.props.FloatProperty(name="Angle")


class MassObjectGroup(bpy.types.PropertyGroup):
    visible: bpy.props.BoolProperty(name="Visible", default=True)
    mass_object_collection: bpy.props.PointerProperty(
        name="Mass Object Collection", type=bpy.types.Collection)
    com_floor_level: bpy.props.FloatProperty(name="Floor Level", default=0.0)
    line_to_floor: bpy.props.BoolProperty(
        name="Draw Line to Floor", default=False)
    color: bpy.props.FloatVectorProperty(name="CoM Marker Color", description="Color of the CoM Marker", default=(
        1, 0, 1), subtype='COLOR', min=0.0, max=1.0)
    com_location: bpy.props.FloatVectorProperty(name="CoM Location", description="Location of the CoM", default=(
        0, 0, 0))
    is_rig_pinned: bpy.props.BoolProperty(
        name="Pin Center of Mass", default=False)
    pinned_rig: bpy.props.PointerProperty(
        name="Pinned Rig", type=bpy.types.Object)
    show_axis: bpy.props.BoolProperty(name="Show Rotation Axis", default=False)
    reference_point: bpy.props.FloatVectorProperty(name="Reference Point", description="Reference point for angle alignment and ballistics ruler.", default=(
        0, 0, 0))
    reference_color: bpy.props.FloatVectorProperty(name="Reference Point Color", description="Color of the Reference Marker", default=(
        0, 1, 0), subtype='COLOR', min=0.0, max=1.0)
    show_reference_point: bpy.props.BoolProperty(
        name="Show Reference Points", default=True)
    ballistics_starting_point: bpy.props.FloatVectorProperty(name="Ballistics Starting Point", description="Starting point of ballistics curve.", default=(
        0, 0, 0))
    ballistics_starting_point_color: bpy.props.FloatVectorProperty(name="Reference Point Color", description="Color of the Reference Marker", default=(
        1, 0, 0), subtype='COLOR', min=0.0, max=1.0)
    calculated_mois: bpy.props.CollectionProperty(type=CalculatedMOI)


class ComProperties(bpy.types.PropertyGroup):
    com_drawing_on: bpy.props.BoolProperty(
        name="CoM Drawing Enabled", default=False)
    mass_density_set: bpy.props.FloatProperty(
        name="Set Density", default=1.0, soft_min=0)


class PhysicsProperties(bpy.types.PropertyGroup):
    selected_mog: bpy.props.StringProperty(
        name="Mass Object Group", description="Selected Mass Object Group to use with Physics Tools")
    initial_angular_velocity: bpy.props.FloatProperty(name="Initial Angular Velocity",
                                                      description="The initial angular velocity used as reference for the duration of the baked frames. Measured in degrees per frame.")
    is_ballistics_preview: bpy.props.BoolProperty(
        name="Preview Ballistics Curve", default=False)
    gravity: bpy.props.FloatProperty(name="Gravity", default=9.807)
    time_of_flight: bpy.props.FloatProperty(
        name="Time of Flight", description="Elapsed frames until it reaches the ballistics reference point.", default=1, min=0.00001)
    frame_start: bpy.props.IntProperty(
        name="Frame Range Start", description="First frame of the physics baking range.")
    frame_end: bpy.props.IntProperty(
        name="End", description="First frame of the physics baking range.")
    frame_rate: bpy.props.IntProperty(name="Frame Rate", default=24, min=1)
