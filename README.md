# Balance Point

## Description

A Blender 3D add-on that visualizes the center of mass of a collection of 
objects.

Ideally, this can help when animating characters to see if they're
realistically balanced.

Has tools to help create and set up objects that have mass with properties for 
density and volume and a way to continuously update the center of mass when 
moving objects/posing armature.

## Getting Started

### Dependencies

* Developed and tested on Blender 3.4, may work on older versions

### Installing

* Install balancepoint.py through Blender Preferences > Add-ons > Install, or
place in scripts > addons folder

* Enable Balance Point in Blender

* Addon will be in View3D > Tools > Balance Point

## Usage

### Center of Mass Settings

* **Add Basic Balance Point Setup**
    
    * Creates a collection that contains a marker for the center of mass, and
    and a basic object that has mass properties. It then sets them up in the
    addon

* **Center of Mass Object**

    * Object to be used as a marker for the center of mass. This object will
    have its location moved whenever the addon updates the center of mass. An
    Empty object with 'In-Front' Viewport Display would be ideal here

* **Floor Center of Mass**

    * (Optional) Another object to be used as marker. Similar to the Center of
    Mass Object, it tracks the center of mass of 'Mass Object Collection', but 
    its Z-position is locked to the 'Floor Level'. This would be where gravity 
    is exerting force on the center of mass towards on the floor

* **Floor Level**
    
    * Z Location of the Floor Center of Mass object. Used where the character's 
    floor level is not at 0

* **Mass Object Collection**

    * Collection where the objects with mass properties are placed. When
    updating, each item in this location with mass properties is used to
    get the location of the center of mass

* **Update On/Off**

    * Toggles continuous updating of center of mass. When set to 'On', the
    center of mass location update occurs whenever an object is moved or
    armature is posed (and whenever the depsgraph is updated) or when the frame
    is changed

    * When set to 'Off', continuous update is disabled

### Mass Properties

* **Mass Properties to Selected**

    * **Mass Properties** - Properties given to objects that can be used to get 
    the center of mass of the whole

        * *active* - Determines if the object is used in calculating the center
        of mass. Can be toggled on and off

        * *density* - Used to calculate mass of the object.

        * *volume* - Used to calculate mass of the object. Can be calculated 
        with 'Calculate volume of selected'

    * **Add/Remove** 
        
        * Add 'Mass Properties' to selected mesh objects. These objects should 
        be placed in the 'Mass Object Collection' in the 'Center of Mass 
        Settings' in order to be used for the 'Center of Mass' location update

    * **Calculate Volume of Selected** 
        
        * Gets the volume of the selected object and sets it in its mass 
        property.

    * **Set Selected CoM to Origins**
        
        * Mass objects need to have their origins set to their individual
        center of masses.
        
        * This performs the Blender operator 'Set Origin > Origin to Center of
        Mass (Volume)' on the selected objects

    * **Set Active to Selected**
        
        * Set the selected object as active/inactive, or toggle between the two.
        
        * Inactive objects are set to display as wireframe, and active objects
        as solid.
    
    * **Selected Mass Objects**
        
        * Shows info about the selected mass objects. You can also edit the
        volume and density of the object manually here
    
    * **Total Mass of Selected**

        * Shows the total mass of the selected mass objects