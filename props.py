import bpy


class MassObjectGroup(bpy.types.PropertyGroup):
    visible: bpy.props.BoolProperty(name="Visible", default=True)
    mass_object_collection: bpy.props.PointerProperty(
        name="Mass Object Collection", type=bpy.types.Collection)
    com_floor_level: bpy.props.FloatProperty(name="Floor Level", default=0.0)
    line_to_floor: bpy.props.BoolProperty(
        name="Draw Line to Floor", default=False)
    color: bpy.props.FloatVectorProperty(name="CoM Marker Color", description="Color of the CoM Marker", default=(
        1, 0, 1), subtype='COLOR', min=0.0, max=1.0)
    use_com_object: bpy.props.BoolProperty(
        name="Use COM Object", default=False)
    com_object: bpy.props.PointerProperty(
        name="COM Object", type=bpy.types.Object)
    is_rig_pinned: bpy.props.BoolProperty(
        name="Pin Rig's COM to COM Object", default=False)
    pinned_rig: bpy.props.PointerProperty(
        name="Pinned Rig", type=bpy.types.Object)
    scale: bpy.props.FloatProperty(name="CoM Marker Scale", default=0.05,
                                   description="Size of the CoM Markers (in meters)", min=0)
    include_secondary_collection: bpy.props.BoolProperty(
        name="Include Secondary Mass Object Collection", default=False)
    secondary_mass_object_collection: bpy.props.PointerProperty(
        name="Secondary Mass Object Collection", type=bpy.types.Collection)
    show_com_object_axis: bpy.props.BoolProperty(
        name="Show Rotation Axis of COM Object", default=False)
    axis_scale: bpy.props.FloatProperty(name="Axis Line Scale", default=2.0,
                                        description="Size of the Axis Scale Line (in meters)", min=0)
    moment_of_inertia: bpy.props.FloatProperty(name="Moment of Inertia", default=2.0,
                                               description="Moment of Inertia of the COM Object's rotation axis", min=0)


class ComProperties(bpy.types.PropertyGroup):
    com_tracking_on: bpy.props.BoolProperty(
        name="CoM Tracking Enabled", default=True)
    com_drawing_on: bpy.props.BoolProperty(
        name="CoM Drawing Enabled", default=False)
    mass_density_set: bpy.props.FloatProperty(
        name="Set Density", default=1.0, soft_min=0)


class CalculatedMOI(bpy.types.PropertyGroup):
    moment_of_inertia: bpy.props.FloatProperty(
        name="Set Density", default=1.0, soft_min=0)
    angle: bpy.props.FloatProperty(name="Angle")


class PhysicsProperties(bpy.types.PropertyGroup):
    selected_mog: bpy.props.StringProperty(
        name="Mass Object Group", description="Selected Mass Object Group to use with Physics Tools")
    align_rotation_p1: bpy.props.FloatVectorProperty(name="Point 1")
    align_rotation_p2: bpy.props.FloatVectorProperty(name="Point 2")
    is_align_preview: bpy.props.BoolProperty(
        name="Preview Alignment", default=False)
    point_scale: bpy.props.FloatProperty(name="Point Scale", default=0.05,
                                         description="Size of the Points (in meters)", min=0)
    initial_angular_velocity: bpy.props.FloatProperty(name="Initial Angular Velocity",
                                                      description="The initial angular velocity used as reference for the duration of the baked frames. Measured in degrees per frame.")
    is_ballistics_preview: bpy.props.BoolProperty(
        name="Preview Ballistics Curve", default=False)
    ballistics_p0: bpy.props.FloatVectorProperty(name="Point 0")
    ballistics_p1: bpy.props.FloatVectorProperty(name="Point 1")
    gravity: bpy.props.FloatProperty(name="Gravity", default=9.807)
    time_of_flight: bpy.props.FloatProperty(
        name="Time of Flight", description="Elapsed frames until it reaches the ballistics reference point.", default=1, min=0.00001)
    frame_start: bpy.props.IntProperty(
        name="Start Frame", description="First frame of the physics baking range.")
    frame_end: bpy.props.IntProperty(
        name="End Frame", description="First frame of the physics baking range.")
    frame_rate: bpy.props.IntProperty(name="Frame Rate", default=24, min=1)
    is_angular_velocity_preview: bpy.props.BoolProperty(
        name="Preview Angular Velocity", default=False)
    calculated_mois: bpy.props.CollectionProperty(type=CalculatedMOI)
