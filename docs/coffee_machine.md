# Tutorial: Coffee Machine

```{note}
In this tutorial we refer to the different parts of the gaphor interface:
{ref}`Model Browser <getting_started:model browser>`, [Toolbox](getting_started:toolbox),
{ref}`Property Editor <getting_started:property editor>`.

Although the names should speak for themselves, you can check out the [Getting
Started](getting_started) page for more information about those sections.
```

## Introduction

In the bustling town of Antville, a colony of ants had formed a Systems
Engineering consulting company called AntSource. They value collaboration,
transparency, and community-driven engineering, and seeks to empower their
employees and customers through open communication and participation in the
systems engineering process.

The engineers at AntSource all have nicknames that reflect the key principles
and concepts of their craft: Qual-ant, Reli-ant, Safe-ant, Usa-ant, and
Sust-ant. They were experts in designing and optimizing complex systems, and
they took pride in their work.

One day, a new client approached AntSource with an unusual request. Cappuccino,
a cat who owned a popular coffee shop called Milk & Whiskers Café, needed a
custom espresso machine designed specifically for felines. Cats just love their
coffee strong, with a creamy and smooth body and topped with the perfect foamy
layer of crema. The ants were intrigued by the challenge and immediately set to
work.

Qual-ant was responsible for ensuring that the machine met all quality
standards and specifications, while Reli-ant was tasked with making sure that
the machine was dependable and would work correctly every time it was used.
Safe-ant designed the machine with safety in mind, ensuring that it wouldn't
cause harm to anyone who used it. Usa-ant designed the machine to be easy and
intuitive to use, while Sust-ant ensured that the machine was environmentally
friendly and sustainable. In this tutorial we follow the adventures of AntSource
to create the perfect kittie espresso machine.

![Two shots of espresso being pulled from an espresso
machine.](images/coffee-machine-double-shot.jpg)

The first thing the ants did was to open Gaphor to the Greeter window and start
a new model with the _SysML_ template. You can now decide to either:
- recreate their work as part of this tutorial. For this, open the SysML Example
model shown at the bottom of the Greeter window
- inspect the result of their work by opening the `coffee-machine`
model located in the `examples` folder.

## Abstraction Levels
Abstraction is a way of simplifying complex systems by focusing on only the most
important details, while ignoring the rest. It's a process of reducing
complexity by removing unnecessary details and highlighting the key aspects of a
system in order to focus on the problem to be solved. It is the key to rigorous
analysis of a system.

To understand abstraction, think about a painting. When you look at a painting,
you see a representation of something - perhaps a person, a landscape, or an
object. The artist has simplified the real world into a set of lines, shapes,
and colors that represent the most important details of the subject. In the same
way, systems engineers, like our friends the ants, use abstraction to represent
complex systems by breaking them down into their essential components and
highlighting the most important aspects.

Abstraction levels refer to the different levels of detail at which a system can
be represented. These levels are used to break down complex systems into
smaller, more manageable parts that can be analyzed and optimized. Said another
way, abstraction levels group portions of a design where similar types of
questions are answered.

There are typically three levels of abstraction in systems engineering and these
are the three levels used in the SysML template:

- Concept Level: Sometimes also called Conceptual Level. Defines the problem
  being solved. This is the highest level of abstraction, where the system is
  described in terms of its overall purpose, goals, and functions. At this
  level, the focus is on understanding the system's requirements and how it will
  interact with other systems.
- Logical Level: Defines a technology-agnostic solution. This is the middle
  level of abstraction, where the system is described in terms of its structure
  and behavior. At this level, the focus is on how the system components are
  organized and how they interact with each other.
- Technology Level: Sometimes also called Physical level. Defines the detailed
  technical solution. This is the lowest level of abstraction, where the system
  is described in terms of its components and their properties. At this
  level, the focus is on the details of the system's implementation.

Each level of abstraction provides a different perspective on the system, and
each level is important for different aspects of system design and analysis. For
example, the conceptual level is important for understanding the overall goals
and requirements of the system, while the physical level is important for
understanding how the system will be built and how it will interact with the
environment.

There is a fourth abstraction level called the Implementation Level that isn't
modeled, which is the concrete built system.

In the upper left hand corner of Gaphor, the Model Browser shows the three top
level packages, dividing up the model in to these three abstraction levels.

![Top level packages of the SysML
template.](images/coffee-machine-top-level-packages.png)

## Pillars

There are four pillars of SysML which help classify the types of diagrams based
on what they represent:

- Behavior: The functionality of a system
- Structure: How a system is formed using parts and connections
- Requirements: Written statements that constrain the system
- Parametric: Enforces mathematical rules across values in the system

If you want to learn more about these four pillars, there is a 30-minute video
by Rick Steiner called [The Four Pillars of SysML](https://youtu.be/998UznK9ogY).

Since Parametric Diagrams are one of the least used diagram types in SysML, we are
going to only focus on the first three. The power of SysML comes in being able
to make relationships between these three pillars. For example, by allocating
behavior like an activity to an element of the structure like a block.

If you expand the top-level Abstraction Level packages in the Model Browser,
each one contains three more packages, one for each pillar. It is in these
packages that we will start to build up the design for the espresso machine.

![Three pillar packages nested under each abstraction level
package.](images/coffee-machine-pillars.png)

## Table of Contents
```{toctree}
coffee_machine_concept
coffee_machine_logical
coffee_machine_wrapup
```
