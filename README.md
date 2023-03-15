# Balance Point

## Description

This add-on for Blender displays the center of mass of a group of objects, 
making it easier to ensure that characters are realistically balanced when 
animating. It includes features for creating and setting up objects with mass 
properties such as density and volume, and can continuously update the center 
of mass as objects are moved or armatures are posed.

## Getting Started

### Dependencies

* Developed and tested on Blender 3.4, may work on older versions

### Installing

* Install balancepoint.py through Blender Preferences > Add-ons > Install, or
place in scripts > addons folder

* Enable Balance Point in Blender

* Add-on will be in View3D > Tools > Balance Point

## Add-on

![Balance Point menu](/images/balance_point_menu.jpg)

### Center of Mass Settings

* **Add Basic Balance Point Setup** - Creates a collection that contains a 
    marker for the center of mass, and a basic object that has mass properties.
    It then sets them in the center of mass settings.

* **Center of Mass Object** - Object to be used as a marker for the center of 
    mass. This object will have its location moved whenever the add-on updates 
    the center of mass. An Empty object with 'In-Front' Viewport Display would 
    be ideal for this.

* **Floor Center of Mass** - (Optional) Another object to be used as marker. 
    Similar to the Center of Mass Object, it tracks the center of mass of 'Mass 
    Object Collection', but its Z-position is locked to the 'Floor Level'. This 
    would be where gravity is exerting force on the center of mass towards on 
    the floor.

* **Floor Level** - Z Location of the Floor Center of Mass object. Used where 
    the character's floor level is not at 0.

* **Mass Object Collection** - Collection where the objects with mass properties
    are placed. When updating, each item in this location with mass properties 
    is used to get the location of the center of mass.

* **Update On/Off** - Toggles continuous updating of center of mass. When set to
    'On', the center of mass location update occurs whenever an object is moved 
    or armature is posed (and whenever the depsgraph is updated) or when the 
    frame is changed.

### Mass Properties

* **Mass Properties to Selected**

    * **Mass Properties** - Properties given to objects that can be used to get 
    the center of mass of the whole.

        * *active* - Determines if the object is used in calculating the center
        of mass. Can be toggled on and off.

        * *density* - Used to calculate mass of the object.

        * *volume* - Used to calculate mass of the object. Can be calculated 
        with 'Calculate volume of selected'.

* **Calculate Volume of Selected** - Gets the volume of the selected object and 
    sets it in its mass property.

* **Set Selected CoM to Origins** - Mass objects need to have their origins set 
    to their individual center of masses. This performs the Blender operator 
    'Set Origin > Origin to Center of Mass (Volume)' on the selected objects.

* **Set Active to Selected** - Set the selected object as active/inactive, or 
    toggle between the two. Active objects are set to display as solid, and 
    inactive objects as wireframes.

* **Selected Mass Objects** - Shows info about the selected mass objects. You 
    can also manually edit the volume and density of the object here.

* **Total Mass of Selected** - Shows the total mass of the selected mass objects