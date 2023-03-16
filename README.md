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

## Usage

### Basic Setup

1. Starting with a simple rigged character

![Step 1](/images/step1.jpg) 

2. Create mesh objects approximating each part of the body. Here, the
    character was sliced with the knife tool at the joints of the armature, and 
    the cut parts were filled in to create manifold meshes.
![Step 2](/images/step2.jpg)


3. With all of the intended mass objects selected, 'Add' mass properties. They
    should each now have 'active', 'density' and 'volume' properties you can 
    edit.

![Step 3](/images/step3.jpg)


4. With the mass objects selected, 'Calculate volume of selected'.

![Step 4](/images/step4.jpg)


5. With mass objects selected, use 'Origin to Center of Mass (volume)' to set
    each individual origin.

![Step 5](/images/step5.jpg)


6. Attach each mass object to their respective bone in the armature. One way
    to do this is to select the object, then the armature, then bone and 
    set the parent to the bone.

![Step 6](/images/step6.jpg)


7. Each mass object should move around with the armature with their individual
    origins intact.

![Step 7](/images/step7.jpg)

8. Make sure the collection containing the mass objects is set, as well as the
    'Center of Mass Object' and optionally the 'Floor Center of Mass Object'.
    Here, two empties are used, but they can be any object.

![Step 8](/images/step8.jpg)

9. Turn 'Update' on. The 'Center of Mass Object' will now track the center of
    mass of the entirety of the character, and the 'Floor Center of Mass Object'
    will follow, but set to the floor level. To stop tracking, set 'Update' to
    off.

![Step 9](/images/step9.jpg)

10. Mass Objects can be hidden, and the character's center of mass is now 
    completely set up.

![Step 10](/images/step10.jpg)

### Using The Center of Mass

* Consider where the character's feet meets the floor. Both feet form a shape
    that is the character **points of contacts** to the floor. The 'Floor
    Center of Mass Object' lies within this shape, and the character would be 
    considered to be balanced for however long they can hold this pose. If this 
    'Floor Center of Mass' is outside this shape of the point of contact, they
    would tip over and fall down.

![Tip 1](/images/tip1.jpg)

* Add objects for the character to interact with by preparing them just as you 
    did with setting up the character mass objects, (giving them mass 
    properties, setting volume and origins). Add them to the 'Mass Object
    Collection'. Set them as 'active' or 'inactive' depending on if you want
    them to effect the entire center of mass. You can also set the density
    to change how it effects the center of mass. Here the character is holding 
    a hammer, with the hammerhead set as a higher density. This gives it more
    weight when calculating the center of mass.

![Tip 2](/images/tip2.jpg)

## Roadmap

* The process for creating and setting up mass objects could be much easier. 
    Possibly by automatically generating them from the armature itself, and
    the user can just change the shape of the generated mass objects

* A way to have the character's center of mass fixed at a location. This would
    simulate a character moving in space, or being airborne.

* Possible physics simulation, by applying forces to the character so they
    can rotate around their center of mass for realistic airborne spinning.