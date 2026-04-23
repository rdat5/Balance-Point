# Balance Point 

Balance Point is a Blender add-on for visualizing and working with [center of mass](https://en.wikipedia.org/wiki/Center_of_mass) in character animation.

## Features

### Center of Mass Visualization

![comviz](/images/center_of_mass.gif)

Once your rigged character is set up, a marker can be drawn in the viewport showing its center of mass as well as a floor marker for the Center of Mass, which can be useful for understanding your character's balance while animating.

### Center of Mass Motion Path

![compath](/images/motion_path.gif)

Calculate and draw a motion path for your character's center of mass

### Ballistic Ruler

![ballrul](/images/ballistics_ruler.gif)

The Ballistic Ruler is a configurable ballistics arc drawn in the viewport, determined by a given starting point, a reference point, time of flight, gravity, and an optional linear damping vector. Your character's root bone can then be baked so that its center of mass follows the arc. This is useful for when your character is airborne (jumping, falling, being thrown, etc.).

### Conservation of Angular Momentum

For the baked ballistics arc, you can specify an initial angle of rotation, and an initial angular velocity. The baking process will take into account the character's moment of inertia tensor to rotate the character in a physically accurate manner by conserving angular momentum:

Baking conserves angular momentum from posing.

![posemoi](/images/posemoi.gif)

Your character's moment of inertia can be used to determine the rate at which they spin during baking.

![moi](/images/moi.gif)

The baking process also handles nutation, which is a wobble or drift in rotation due to an asymmetric distribution of mass.

![nutation](/images/nutation.gif)

### More Features

- Customize viewport drawing
- Add multiple mass collections per group
- Track objects to the center of mass
- Bake the root bone to track the center of mass for root motion

## Getting Started

### Blender Version Support

* Developed and tested on Blender 5.0.1

### Installing

* Download the latest release

* Install through Blender Preferences > Add-ons > Install

* Enable Balance Point in Blender

* Add-on will be in View3D > Sidebar > Balance Point

## Usage

For help on getting started and using Balance Point, check out the [Balance
Point wiki](https://github.com/rdat5/Balance-Point/wiki)

## Authors and acknowledgment

Inspired by A. Shapiro, S.H. Lee, Practical Character Physics For Animators,
IEEE Computer Graphics and Applications, July/August 2011
([pdf](https://www.arishapiro.com/Practical_Character_Physics_Shapiro_Lee.pdf),
[video](https://www.arishapiro.com/practical_character_physics.mov),
[bibtex](https://www.arishapiro.com/bibtex/practicalcharacterphysics.bib))
[Youtube mirror](https://www.youtube.com/watch?v=s1jpnnqPsMk)

***

If you find this add-on useful, consider donating to help me maintain it and further improve it

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/R6R2JHVA9)