# Tutorial: Coffee Machine

```{note}
In this tutorial we refer to the different parts of the gaphor interface:
{ref}`Model Browser <getting_started:model browser>`, [Toolbox](getting_started:toolbox),
{ref}`Property Editor <getting_started:property editor>`.

Although the names should speak for themselves, you can check out the [Getting
Started](getting_started) page for more information about those sections.
```

In this tutorial we create a simple SysML model of an espresso machine. Why
espresso? Well, we like our coffee strong, with a creamy and smooth body and
topped with a foamy layer of crema. Yum!

![Two shots of espresso being pulled from an espresso
machine](images/coffee-machine-double-shot.jpg)

Open Gaphor to the Greeter window and start a new model with the _SysML_ template.

## Abstraction Levels

Abstraction is the method of removing details to focus on the problem that needs
to be solved. It is the key to rigorous analysis of a system. Abstraction Levels are
groupings of portions of a design so that similar types of questions are
answered at each level. The SysML template is divided into three abstraction
levels:

- Concept Level: Defines the problem being solved
- Logical Level: Defines a technology-agnostic solution
- Technology Level: Defines the detailed technical solution

There is a fourth abstraction level called the Implementation Level that isn't
modeled, which is the concrete built system.

In the upper left hand corner of Gaphor, the Model Browser shows the three top
level packages, dividing up the model in to these three abstraction levels.

![Top level packages of the SysML
template](images/coffee-machine-top-level-packages.png)

## Pillars

There are four pillars of SysML which help classify the types of diagrams based
on what they represent:

- Behavior: The functionality of a system
- Structure: How a system is formed using parts and connections
- Requirements: Written statements that constrain the system
- Parametrics: Enforces mathematical rules across values in the system

If you want to learn more about these four pillars, there is a 30-minute video
by Rick Steiner called [The Four Pillars of SysML](https://youtu.be/998UznK9ogY).

Since Parametrics Diagrams are one of the least used diagram types in SysML, we are
going to only focus on the first three. The power of SysML comes in being able
to make relationships between these three pillars. For example, by allocating
behavior like an activity to an element of the structure like a block.

If you expand the top-level Abstraction Level packages in the Model Browser,
each one contains three more packages, one for each pillar. It is in these
packages that we will start to build up the design for the espresso machine.

![Three pillar packages nested under each abstraction level
package](images/coffee-machine-pillars.png)

## Concept Level

The concept level defines the problem we are trying to solve. For the espresso
machine, we are going to use diagrams at this abstraction level to answer questions like:

- Who will use the machine and what are their goals while using it?
- What sequence of events will a person take while operating the machine?
- What things surround and interact with the machine?
- What are the needs of others like those marketing, selling, manufacturing, or buying the machine?

### Use Case Diagram



The use case diagram
In the
A barista interacts with the espresso machine.
The barista is provided a simple interface with a few push buttons.


The espresso machine consists of a few components:

- A heating device
- a pressure device, we need around 9 bar
- A piston that needs to be filled with ground coffee.
- something to capture spilled liquid
- a water reservoir
- a power supply

External devices include:

- a coffee grinder
- a cup

## Define activities

## Component diagram

## Constraints

- pressure should not exceed _n_ bar
- no short circuits if water leaks
- should turn off after _n_ minutes of interactivity


## What's next

Most espresso machines feature a milk steaming device.
