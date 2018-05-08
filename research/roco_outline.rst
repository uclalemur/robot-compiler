Goal
=============================
*   Enable the general public to design and fabricate robots through automated processes

    *   Codesign across multiple domains through a simple, visual UI 

    *   Codesign using preconfigured, functionally defined objects

        *   If want a controllable robot, create a chassis and servos, it'll automatically add the microcontroller/network card and ensure the chassis is large enough

    *   Fabricate through low-cost, accessible mediums with minimal assembly

    *   Fabricate into multiple mediums using one design

    *   Establish library of reusable, reconfigurable, modular robotic designs

Audience
=============================
*   General public with computer, internet, and printer access

    *   Not for tablet/smartphone b/c input methods + screen size

    *   Non-professional b/c won't support that level of customization

    *   Non-hobbyist b/c shouldn't need experience

    *   Non-very-young-child b/c they won't be able to fabricate

User Flow
=============================
*   Access

    *   Click/type link to home page

    *   Click link to access RoCo application through browser
*   Tutorial (Optional)

    *   Guides user in creating a simple two wheeled robot

    *   Explains interface through highlighting and popup textboxes
*   Design

    *   Design wheeled robot

        *   Add rectangular prism (Geometry)

        *   Add servo (Geometry, Electronic, Software)

            *   Auto add MCU (Geometry, Electronic, Software)

                *   Auto connect servo <-> MCU

            *   Auto add battery (Geometry, Electronic)

                *   Auto connect MCU <-> battery

        *   Connect MCU to rectangular prism[a] (Geometry)

        *   Connect battery to rectangular prism (Geometry)

        *   Add circle (Geometry)

        *   Connect circle to servo (Geometry)

        *   Duplicate wheel (Geometry, Electronic, Software)

        *   Connect left wheel to left side of prism (Geometry)

            *   Auto add cutout (Geometry)

        *   Connect right wheel to right side of prism (Geometry)

            *   Auto add cutout (Geometry)

    *   Design web controller

        *   Add web controller (Software)

            *   Auto add ESP8266 (Geometry, Electronic, Software)

                *   Auto connect ESP8266 <-> MCU

        *   Add buttons to web controller (Software)

            *   Auto add function (Software)

                *   Auto connect button <-> function

        *   Connect function to servo (Electroprogrammatic)

    *   Different orderings must be permissible
*   Fabricate

    *   Paper robot

        *   Materials/Fabrication requirements

            *   Paper, Paper cutter (optionally)

            *   Arduino, ESP8266, Continuous Servo (2), Battery, Wire to upload code

        *   Mechanical

            *   Tabs

            *   Printable SVG

            *   Laser cuttable SVG

        *   Electroprogrammatic

            *   Wiring Instructions

            *   Text files for MCU

            *   Text files for web controller

    *   Wood robot

        *   Materials/Fabrication requirements

            *   Wood sheets, Wood cutter

            *   Arduino, ESP8266, Continuous Servo (2), Battery, Wire to upload code

        *   Mechanical

            *   Fingerjoints

            *   Cuttable SVG

        *   Electroprogrammatic

            *   Wiring Instructions

            *   Text files for MCU

            *   Text files for web controller
*   Simulate

    *   ...

Related/Alternative Approaches
=============================
*   Geometry Generation

    *   First version of RoCo relied on using an algorithm to input edge/angle constraints and output nonlinear equations representing each vertex coordinate. This resulted in a system of 10^2 nonlinear equations for simple robots, growing exponentially; thus, it is infeasible to solve.

    *   We will embed edge/angle constraints inside RoCo's representation of geometry. Then we will input the edge/angle constraints into Sympy which will output edge lengths and coordinates. Then we will input edge lengths/angles into a BFS-style algorithm to generate vertex coordinates.
*   Geometry Generation

    *   It is not clear whether it is better to compose 3D object from many polygons or to create parameterized 3D objects as a primitive.

    *   3D object from many polygons will have issues of defining the rotation of one face relative to another face.

    *   Parameterized 3D object primitive has issues of how to specify all interior angles in a reasonable fashion; this is unlike how to denote all interior angles of a parameterized 2D object because a 2D object always has equal number of angles and sides.

    *   3D object has edges and polygons. polygons are groups of edges

    *   Difficult to implement this using vertex groups, because if we only select the vertices which represent the edge, then set this group's length to double (using scale mechanisms), and the object is a cube subdivided 3 with the group vertices being the center strip, it will not work.

    *   Model vertex as only a connection point of edges, dont know where the vertex itself is, only know edge lengths and orientation of edge from relative to vertex

    *   Vertex has list of (edge, angle) pairs. Angle is xyz rotation. edge is an object with a length and has list of vertices. when doing dfs to get vertices, maintain knowledge of angle. 

    *   a lot of these approaches have problem of not knowing what is a face and what isnt.
*   Parameterization

    *   Parameterization in RoCo was previously treated at the Component level (affecting geometry, electronics, and software).

    *   Parameterization is only relevant for geometry because circuits will not be customized by users and software is inherently parameterized.

Architectural Model
=============================
*   Three Phases of RoCo

    *   Design/Generation

        *   Mechanical

            *   UI

                *   3D physical view

                *   Panel of preconfigured objects

                *   Hide as much unnecessary functionality as possible

            *   Adding element to mechanical will add to electrical 

            *   Parameterization

            *   Modifiers (cutouts)?

            *   Understanding of material

            *   Colors

        *   Electroprogammatic

            *   UI

                *   2D node view

                *   Nodes have interfaces

                *   Connect interfaces according to functionality (user input -> controller program -> servo) (skips the board, skips the web controller specification)

                *   Hide as much unnecessary functionality as possible

            *   Adding to electrical will add to programmatic

            *   Support minimal set of common, widely available, affordable electronics (subset of Adafruit) (ESP8266, continuous rotation servo) (geometry will be immutable)

            *   Output to Arduino + RPI

    *   Fabrication

        *   Mechanical

            *   Accounts for material (paper -> tabs, wood -> finger joints, 3d -> snapfits)

            *   Ensuring fabricability

                *   Face intersection

        *   Electroprogrammatic 

            *   Account for the electrical circuit's software

            *   Ensuring fabricability

                *   Power source to power

                *   Electrical circuits to run code on

                *   Code dependencies

    *   Simulation/Control

        *   Mechanical/Electroprogrammatic

            *   Control physical robot through adjusting values within Blender
*   Python Addon to Blender using Sympy
*   Documentation through Sphinx + RTD; Github for main repo; GitLabs as backup
*   No install/web accessibility through AWS AppStream 2.0

Abstraction Model
=============================

*   Supercomponent: the new object being constructed

    *   Component: a configurable objects 

        *   Field: an orthogonal design domain 

            *   Feature: a functionally defined attribute 

                *   Functional: the things which actually implement the functionality of the component 

                    *   Data: the user-specified inputs

                    *   Modifiers: how users change the inherent  

                    *   Composable: the fabricable object

                *   Interfaces: the input/output of the blackbox feature

                    *   Data: what is currently connected, how many connections can be supported

                    *   Constraints: how other components change the data

                *   Prerequisites: other feature(s) of a different type that this feature require to exist?

                *   Dependencies: other feature(s) of the same type that this feature requires to actually work

        *   Field: Mechanical

            *   Feature: Geometry

                *   Functionals: N-gon

                    *   Data: Edge Length, Angle, Material

                    *   Modifiers: Cutouts

                    *   Composable: Bmesh (Vertices, Edges, and Faces)

                *   Interfaces: N-gon's edges and angles

                    *   Data: Edge, Angle

                    *   Constraints: Edge, Angle

                *   Prerequisites: N/A

                *   Dependencies: 

            *   Feature: Dynamics (armature, etc)

                *   ...

        *   Field: Electroprogrammatic

            *   Feature: Electronic

                *   Functionals: Pinout Diagram

                    *   Data: Pins, Connections

                    *   Modifiers: N/A

                    *   Composable: Wiring Diagram/Instructions

                *   Interfaces: Pins

                    *   Data: Wired connection

                    *   Constraints: N/A

                *   Prerequisites: Geometry

                *   Dependencies: (battery, MCU)

            *   Feature: Software

                *   Functionals: Program

                    *   Data: Nodes and connections (Variables, initializations, generalized functions)

                    *   Modifiers: N/A

                    *   Composable: Text

                *   Interfaces: Input/output

                    *   Data: Text?

                    *   Constraints: N/A

                *   Prerequisites: Electronic

                *   Dependencies: (libraries)

Implementation Model
=============================
*   N-gon

    *   Properties

        *   Mechanical 

            *   Blender internal geometry data (vertex position, object location/rotation, Blender’s vertex group...)

            *   List of geometric features (edges, angles)

            *   List of constraints

    *   Interfaces

        *   List of constraints

*   Electroprogammatic

*   Constraints

    *   Edge Constraint

    *   Angle Constraint
    
*   Interfaces

    *   Supercomponent

    *   Single Blender object

Resources and Examples
=============================

*   Parameterized Blender

    *   Sverchok_ 

        .. _Sverchok: https://wiki.blender.org/index.php/Extensions:2.6/Py/Scripts/Nodes/Sverchok

    *   Archimesh_ 

        .. _Archimesh: https://youtu.be/WeAlm6_jVDY

    *   Archipack_

        .. _Archipack: https://www.youtube.com/watch?v=nf8QHISjRLY https://github.com/s-leger/archipack/wiki/Parametric-Objects-developper-guide

    *   `Generating mesh`_

        .. _`Generating mesh`: http://sinestesia.co/blog/tutorials/python-2d-grid/

    *   `Modifying mesh`_

        .. _`Modifying mesh`: https://stackoverflow.com/questions/37808840/selecting-a-face-and-extruding-a-cube-in-blender-via-python-api

    *   `Force change mode`_

        .. _`Force change mode`: https://blender.stackexchange.com/questions/27482/is-there-a-way-to-explicitly-set-the-mode-in-python

*   UI/UX Overridden Example

    *   `Fluid Designer`_
    
        .. _`Fluid Designer`: https://www.microvellum.com/dt_gallery/fluid-designer-screen-shots/

    *   `Overriding User Prefs`_ 

        .. _`Overriding User Prefs`: https://blender.stackexchange.com/questions/283/changing-user-preferences-via-console

    *   `Tutorial to override Blender UI in Python`_

        .. _`Tutorial to override Blender UI in Python`: https://www.youtube.com/watch?v=2j75AM1Mttc

    *   `Graphical Programming Sample`_

        .. _`Graphical Programming Sample`: https://www.youtube.com/watch?v=B32gktrRvKs

*   Robots

    *   `IBM TJBot`_

        .. _`IBM TJBot`: http://delivery.acm.org/10.1145/3060000/3052965/ea381-dibia.pdf?ip=131.179.2.204&id=3052965&acc=ACTIVE%20SERVICE&key=CA367851C7E3CE77%2E79535EF926D6BC05%2E4D4702B0C3E38B35%2E4D4702B0C3E38B35&__acm__=1525810293_e007cd17051356d03b82c22e1c0dafd5

    *   `Robot Designer demo; has geometry, muscles, kinematics, sensors, constraints, etc`_
        
        .. _`Robot Designer demo; has geometry, muscles, kinematics, sensors, constraints, etc`: https://www.youtube.com/watch?v=_ii0CVzVcsA&list=PLFfa5EHopIFosLhZa3HxGQzo1JyM-MhUq

    *   `Reading from Arduino into Blender`_
        
        .. _`Reading from Arduino into Blender`: https://www.youtube.com/watch?v=tyH8HswHh0Q

    *   `Control physical robot arm from within Blender`_

        .. _`Control physical robot arm from within Blender`: http://justindailey.blogspot.com/2011/03/real-time-controlled-robotic-arm.html

    *   `Robot with multiple motors being controlled from within Blender`_ 
        
        .. _`Robot with multiple motors being controlled from within Blender`: https://www.youtube.com/watch?v=XqMHoJ-ihdw

    *   `Controlling 3D Printed Thor arm from within Blender`_

        .. _`Controlling 3D Printed Thor arm from within Blender`: https://www.youtube.com/watch?v=DmqUdcp0udM

    *   `Controlling Arduino + robot arm from Blender`_ 

        .. _`Controlling Arduino + robot arm from Blender`: https://www.youtube.com/watch?v=mHZBFZSklqk

    *   `Demo of 3D cube + other shapes being exported to SVG for physical fabrication; includes tabs`_

        .. _`Demo of 3D cube + other shapes being exported to SVG for physical fabrication; includes tabs`_: https://www.youtube.com/watch?v=s123RTkCi0M

    *   `Physical paper head`_
        
        .. _`Physical paper head`: https://www.youtube.com/watch?v=Y6ECUuwHA4s

FAQ
=============================
*   How do I start Blender on Mac with terminal available for debugging?

    *   https://docs.blender.org/manual/en/dev/render/workflows/command_line.html::

            cd /Applications/Blender
            ./blender.app/Contents/MacOS/blender

    *   How do I install Sympy in Blender for development? (Mac)::
   
            cd /Applications/Blender/blender.app/Contents/Resources/2.79/python/lib/python3.5/site-packages
            git clone git://github.com/sympy/sympy.git
            mv sympy/sympy sympy2
            rm -rf sympy
            mv sympy2 sympy
            git clone https://github.com/fredrik-johansson/mpmath.git
            mv mpmath/mpmath mpmath2
            rm -rf mpmath
            mv mpmath2 mpmath

    *   How do I test that Sympy installed correctly?::

            from sympy import   x = Symbol('x')
            limit(sin(x)/x, x, 0)

    *   Where is startup file?::

            cd /Users/quentintruong/Library/Application\ Support/Blender/2.79/config

Blender API Tips
=============================
*   bpy.data.objects.keys() # list of all available objects

*   bpy.data.objects['Cube'].select = True # selects 'Cube' object

*   bpy.ops.object.editmode_toggle() # toggle edit mode

*   bpy.ops.object.mode_set(mode='EDIT', toggle=False) # force edit mode

*   bpy.ops.transform.resize(value = (1, 2, 3)) # scale currently selected item; should not be used for editing mesh

*   bpy.context.object.data.update() # update data and view; if excluded, will not see update in 3D view until you click the 3D view

*   bpy.data.screens['Scripting'].areas[1].type = 'VIEW_3D' # will change area type without need for context

*   bpy.ops.wm.window_duplicate() # creates new screen and swaps to it

*   py.utils.unregister_class(bpy.types.Panel.__subclasses__()[1]) # unregisters (hides) subpanels

*   bpy.data.node_groups[NODETREENAME].nodes[0].custom_properties.int_value # to access custom properties in node
