Parameterized (Object)
====================================
*   has parameters

*   has constraints

Component (Parameterized)
====================================
*   represents an element of a device

*   has interfaces

*   has composables

*   has hierarchical constraints

*   add_subcomponent() - supposed to be able to add subcomponents which are other components and add constraints and parameters on these components

*   add_connection()

*   add_interface()

*   inherit_interface()

*   add_parameter()

*   set_parameter()

*   assemble() will add composable

Composable (Object)
====================================
*   represents an interface for producing output

*   to combine components of a certain type to generate some output

*   when do composables get added?

Connection (Object)
====================================
*   represents a connection between interfaces

*   has from_interface

*   has to_interface


Interface (Object)
====================================
*   represents a collection of ports

*   has ports


Port (Parameterized)
====================================
*   represents a single input or output

Make
====================================
*   make()

    *   reset()
    
        *   not truly implemented
        
    *   resolve_subcomponents()
    
        *   add subcomponents to this component
        
        *   inherit parameters from subcomponents to this component
        
        *   inherit constraints from subcomponents to this component
        
    *   eval_hierarchical_constraints()
    
        *   substitutes value of variables from hierarchical constraints
        
        *   records solved value
        
    *   eval_subcomponents()
    
        *   inherit composables from subcomponents to this component
        
    *   eval_interfaces()
    
        *   inherit interfaces from component to this components' composables 
        
        *   not truly implemented
        
    *   eval_connections()
    
        *   connect ports between subcomponents
        
        *   connect ports between subcomponents' composables
        
        *   create any necessary constraints to satisfy ports
        
    *   assemble()
    
        *   overridden by some base components
        
        *   creates composables
        
        *   adds interfaces
        
        *   adds faces
        
    *   solve()
    
        *   solve variable values based on equality constraints
        
    *   check_constraints()
    
        *   verifies constraints are not broken
        
        *   not truly implemented
        

Sample
====================================
Code::
    from roco.api.component import Component
    c = Component()
    c.add_subcomponent("R1", "Rectangle")
    c.make_output()

