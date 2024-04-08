---
file_format: mystnb
---

# Coffee Machine: Logical Level

## Introduction

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
Pump, Water Heater, Group Head, and Portafilter. The HMI receives the button
press from the barista and then sends a command to the Controller. The
Controller then commands the Water Heater to start, and
once the water has reached the correct temperature, the Controller commands
the Pump to start. The water would then be pumped through the
Group Head and into the Portafilter, brewing the coffee. The diagram shows
the flow of information and actions between the different logical blocks, and
help to ensure that the behavior that each block provides is properly connected
and integrated into the system.

```{diagram} Functional Boundary Behavior
:model: coffee-machine
```

From the Logical package, expand the Behavior package in the Model Browser and
double-click on the diagram named Functional Boundary Behavior. Additional
swimlanes can be added by clicking on the swimlanes and add additional
partitions in the Property Editor. The name of the partition before the colon can
also be changed in the Property Editor. The names of the Blocks can be changed in
the Structure package, as was explained in the [Domain Diagram section](coffee_machine_concept.md#domain-diagram).

Additional Object Flows, pins (pay attention to inputs vs outputs), and actions can be
created using the Toolbox. The Parameter Nodes which are attached to the Activity on the
very left and right of the diagram are created and renamed created by clicking on the
Activity and modifying them in the Property Editor.

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
:alt: State machine diagram showing logical states including on and off
```

Open the Logical States diagram and add a region to the On state via the Property Editor.
Next use the Toolbox to add the additional substates and transition. Guards for the
transitions, shown surrounded by brackets, are added by selecting the transition and
adding the guard in the Property Editor.

The logical state machine diagram for the coffee machine shows these states,
and the different conditions that trigger the transitions. This helps the ants
designing the machine to understand how the coffee machine works and ensure
that it functions properly.

## Logical Structure

The logical structure shows which logical blocks the espresso machine is made
up of. Since we are at the logical level, these blocks should be agnostic to
technical choices.

The following logical blocks are part of the espresso machine:
- Water tank
- Water pump
- Water heater
- Portafilter
- Controller
- Group head
- HMI

Each block represents a key portion of the espresso machine, and the
containment relationship is used between the espresso machine and its logical
parts.

```{diagram} Logical Structure
:model: coffee-machine
:alt: Block definition diagram showing the coffee machine and its logical parts
```

- Water tank: The water tank is a container that stores the water used in the
  espresso machine. It typically has a specific capacity and is designed for easy
  filling and cleaning. The water tank supplies water to the water pump when
  needed.

- Water pump: The water pump is responsible for drawing water from the water tank
  and creating the necessary pressure to force the water through the coffee
  grounds in the portafilter. It plays a crucial role in the espresso extraction
  process by ensuring a consistent flow of water.

- Water heater: The water heater, also known as the boiler or heating element, is
  responsible for heating the water to the optimal temperature for brewing
  espresso. It maintains the water at the desired temperature to ensure proper
  extraction and flavor.

- Portafilter: The portafilter is a detachable handle-like device that holds the
  coffee grounds. It is attached to the espresso machine and acts as a filter
  holder. The water from the pump is forced through the coffee grounds in the
  portafilter to extract the flavors and create the espresso.

- Controller: The controller, often a microcontroller or a dedicated circuit
  board, is the brain of the espresso machine. It manages and coordinates the
  operation of various components, such as the water pump, water heater, and HMI,
  to ensure the correct brewing process. It monitors and controls temperature,
  pressure, and other parameters to maintain consistency and deliver the desired
  results.

- Group head: The group head is a part of the espresso machine where the
  portafilter attaches. It provides a secure connection between the portafilter
  and the machine, allowing the brewed espresso to flow out of the portafilter
  and into the cup. The group head also helps to maintain proper temperature and
  pressure during the brewing process.

- HMI (Human-Machine Interface): The HMI is the user interface of the espresso
  machine. It provides a means for the user to interact with the machine, usually
  through buttons, switches, or a touchscreen. The HMI allows the user to select
  different brewing options, adjust settings, and monitor the status of the
  machine. It provides feedback and displays information related to the brewing
  process, such as brewing time, temperature, and cup size selection.

We didn't make any technical choices at this time, for example we didn't
specify which type of controller, the pump capacity, or the model of the
group head. These details will be defined once we get to the Technology level.

The ants need more of your help to update the Logical Structure diagram so that
it matches the one above.

## Logical Boundary

The Logical Boundary is a type of Internal Block Diagram that represents the
internal structure of a system, illustrating the relationships between its
internal components or blocks. It helps to visualize how these blocks interact
and exchange information within the system. The term boundary used here means a
clear box view inside the espresso machine at the logical boundary. It uses
part properties of the blocks that were in the Logical Structure diagram above.

```{diagram} Logical Boundary
:model: coffee-machine
:alt: Internal block diagram showing the clear box view of the espresso machine
```

The interactions between the part properties inside the espresso machine are
shown as ItemFlows on the Connectors.

-  Water: Represents the flow of water from the water tank to the water pump.
-  On/Off: Represents the command or signal to turn the espresso machine on or off.
-  Volume Adjustment: Represents the user-selected volume adjustment for the coffee output.
-  Pressurized Water: Represents the water flow under pressure for extracting coffee.
-  Heat Command: Represents the command or signal to activate the water heater and initiate the heating process.
-  Temperature: Represents the feedback signal indicating the current temperature of the water.
-  Hot Pressurized Water: Represents the pressurized hot water for brewing coffee.
-  Coffee Water Mixture: Represents the mixture of hot water and coffee grounds during the brewing process.


```{attention}
Notice that we aren't actually showing anything entering or leaving the
boundary of the espresso machine, like the input from the barista or the
resulting coffee. Gaphor doesn't current support adding ports to the boundary
of an internal block diagram, but hopefully we'll be able to add support soon!
```

These item flows capture the essential interactions and exchanges within the
espresso machine. They represent the flow of water, control signals,
temperature feedback, and the resulting coffee water mixture. The item flows
illustrate the sequence and connections between the various components,
allowing for a better understanding of how the machine functions as a whole.

Once again, help the ants by updating the Logical Boundary diagram so that it
matches the one above.

## Logical Requirements
Logical requirements refer to the high-level specifications and functionalities
that describe what a system or product should accomplish without specifying how
it will be implemented. These requirements focus on the desired outcomes and
behavior of the system rather than the specific technical details.

We have also already defined the behavior and the structure of the espresso
machine at the logical level, so the main task now is to translate that
information in to words as requirement statements.

```{tip}
If you need help writing good requirements, the [INCOSE Guide to Needs and
Requirements](https://portal.incose.org/commerce/store?productId=INCOSE-GUIDENEEDSREQ)
and the [Easy Approach to Requirements Syntax](https://alistairmavin.com/ears/)
are recommended resources.
```

We use the Derive Requirement relation from the Logical Requirement to the
Concept Requirements that we previously created. The direction of this
relationship is in the derived from direction, which might be opposite to what
you are used to where the higher level requirement points to the lower level
requirement.

Here we derive two requirements:

- Controller commands heat up
- 900kPa of water pressure

```{diagram} Logical Requirements
:model: coffee-machine
:alt: Logical requirements for the controller command and the water pressure derived from concept requirements
```

Update the Logical Requirements diagram with these requirements. If you want,
you can also develop additional requirements for all the logical behavior and
structure that we specified in the other diagrams.
