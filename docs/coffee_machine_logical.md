---
file_format: mystnb
---

# Coffee Machine: Logical Level

At the logical Level, we'll define a technology-agnostic solution. This is the
middle level of abstraction, where the system is described in terms of its
structure and behavior. At this level, the focus is on how the system
components are organized and how they interact with each other.

## Functional Boundary Behavior

A Functional Boundary Behavior diagram is a type of SysML Activity diagram used
to show the interactions between different logical blocks. The
swim lanes divide the diagram into different areas, each representing a
different functional block or component.

In this case, the diagram includes swimlanes for the HMI, Controller, Water
Pump, Water Heater, Grouphead, and Portafilter. The HMI receives the button
press from the barista and then sends a command to the Controller. The
Controller then commands the Water Pump and Water Heater to start, and
once the water has reached the correct temperature, the Controller commands
the Pump and Heater to start. The water would then be pumped through the
Grouphead and into the Portafilter, brewing the coffee. The diagram shows
the flow of information and actions between the different logical blocks, and
help to ensure that the behavior that each block provides is properly connected
and integrated into the system.

```{diagram} Functional Boundary Behavior
:model: coffee-machine
```

From the Logical package, expand the Behavior package in the Model Browser and
double-click on the diagram named Functional Boundary Behavior. Additional
swimlanes can be added by clicking on the swimlanes and add additional
partitions in the Property Editor.

In the Structure package, right-click on the Blocks with the B symbol and rename
them from the context menu so that the names of the Logical Blocks in each
swimlane are correct. The name of the partition before the colon can also be
changed in the Property Editor.

Additional Object Flows, pins, and actions can be created using the Toolbox.
The Parameter Nodes which are attached to the Activity on the very left and right
of the diagram are renamed and created by clicking on the Activity and modifying
them in the Property Editor.

## Logical State Machine

The logical state machine for the coffee machine is a diagram that shows the
different states and transitions that the machine goes through to make coffee.
In this case, there are two main states: On and Off.

When the coffee machine is turned on, it enters the On state. Inside the On
state, there are some substates, starting with the heat water state. The
machine will transition from the heat water state to the ready state when the
temperature reaches the set point.

Once the machine is in the ready state, the user can select one or two cup
mode. Depending on the mode selected, the machine will transition to either the
one cup mode or two cup mode.

```{diagram} Logical States
:model: coffee-machine
```
Open the Logical States diagram and use the Toolbox to add the additional
substates and transition. Guards for the transitions are added by selecting
the transition and adding the guard in the Property Editor.

The logical state machine diagram for the coffee machine shows these states,
and the different conditions that trigger the transitions. This helps the ants
designing the machine to understand how the coffee machine works and ensure
that it functions properly.
