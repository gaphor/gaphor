---
file_format: mystnb
---

# Coffee Machine: Concept Level

## Introduction

The concept level defines the problem we are trying to solve. For the espresso
machine, we are going to use diagrams at this abstraction level to answer questions like:

- Who will use the machine and what are their goals while using it?
- What sequence of events will a person take while operating the machine?
- What are the key features and capabilities required for the machine to perform its intended function?
- What are the design constraints and requirements that must be considered when designing the machine?
- What are the key performance metrics that the machine must meet in order to be considered successful?
- How will the machine fit into the larger context of the café, and how will it
  interact with other systems and components within the café?
- What are the needs of others like those marketing, selling, manufacturing, or buying the machine?

At this level, the focus is on understanding the big picture of the espresso
machine and its role within the café system. The answers to these questions will
help guide the design and development of the machine at the logical and
technology levels of abstraction.

## Use Case Diagram

First the ants work on the behavior of the system. Expand the Behavior package
in the Model Browser and double-click on the diagram named Use Cases.

A use case diagram is a type of visual representation used in systems
engineering to describe the functional requirements of a system, such as an
espresso machine. In the context of the espresso machine, a use case diagram
would be used to identify and define the different ways in which the machine
will be used by its users, such as the café staff and customers.

The diagram would typically include different actors or users, such as the
barista, the customer, and possibly a manager or maintenance technician. It
would also include different "use cases" or scenarios, which describe the
different actions that the users can take with the machine, such as placing an
order, making an espresso, or cleaning the machine.

The use case diagram helps to ensure that all the necessary functional
requirements of the espresso machine are identified and accounted for, and that
the system is designed to meet the needs of its users. It can also be used as a
communication tool between the different stakeholders involved in the
development of the machine, such as the ants and Cappuccino the cat.

The ants need your help updating the diagrams, so let's get started:

1. Double-click on the actor to pop up the rename dialog, and replace User with
   Barista.
2. Update the name of the oval Use Case from Use Case #1 to Brew espresso.
3. Update the name of the rectangle Block from Feature to Espresso Machine

A barista interacts with the espresso machine.
The barista is provided a simple interface with a few push buttons.

In this particular use case diagram, we have one actor named Barista and one
use case called Brew espresso, which is allocated to a block called Espresso
Machine. The actor, in this case, is a cat barista who interacts with the
system (an espresso machine) to accomplish a particular task, which is brewing
espresso.

```{diagram} Use Cases
:model: coffee-machine
:alt: Use case diagram showing an actor named Barista and a use case called Brew espresso
```

The use case Brew espresso represents a specific functionality or action that
the system (the Espresso Machine block) can perform. It describes the steps or
interactions necessary to complete the task of brewing espresso, such as
selecting the appropriate settings, starting the brewing process, and stopping
the process once it's complete.

The use case diagram shows the relationship between the actor and the use case.
It is represented by an oval shape with the use case name inside and an
association with the actor. The association represents the interaction from the
actor to the use case.

## Domain Diagram

A domain diagram is a graphical representation of the concepts, terms, and
relationships within a specific domain. In the case of a coffee shop, a domain
diagram could represent the key elements and relationships within the coffee
shop domain.

The following is a domain diagram that builds upon the context diagram with
additional blocks:
- Barista
- Coffee Machine
- Roasted Coffee
- Coffee Grinder
- Water Supply
- Customer

Each block in the Block Definition Diagram (bdd) represents a key concept within the coffee shop domain, and the
containment relationship is used between the domain and the blocks to show
that they are part of the domain.

```{diagram} Espresso Domain
:model: coffee-machine
:alt: Block Definition Diagram showing hierarchy of blocks in the Coffee Shop domain
```

The Barista block is responsible for preparing and serving the coffee to the
customers. The Roasted Coffee block contains the types of coffee available for
the barista to use. The Coffee Grinder block grinds the roasted coffee beans to
the desired consistency before brewing. The Water Supply block contains the
water source for the coffee machine, and finally the Customer block represents
the person who orders and receives the coffee.

The ants need more of your help to rename the Feature Domain diagram and update it
so that it matches the one above. Make sure that "Profile: SysML" is selected in the
top-left corner of the Gaphor user interface. The names of the blocks can be changed
directly in the diagram, but the name of the bdd can only be changed in the Model Browser.
In the Structure package, right-click on the Blocks with the B symbol and rename
them from the context menu. Also remember that you can use [auto-layout](first_model.md#adding-relations)
to align and distribute all elements.

The domain diagram provides a high-level view of the coffee shop domain and the
key concepts and relationships involved in it. It can be a useful tool for
understanding the relationships between different elements of the domain and
for communicating these relationships to others.

## Context Diagram

The context diagram is a high-level view of the system, and it shows its
interaction with external entities. In the case of a coffee machine, a context
diagram provides a clear and concise representation of the system and its
interactions with the external environment.

The context diagram for a coffee machine shows the coffee machine as the
system at the center, with all its external entities surrounding it. The
external entities include the barista, the power source, the coffee
grinder, and the water source.

```{diagram} Espresso Context
:model: coffee-machine
:alt: Block definition diagram showing context of the coffee shop with external entities
```

The ants need more of your help to rename the Feature Context diagram and update it
so that it matches the one above. To create the specific arrows shown, use an Association
entity, then toggle Enable Item Flow to on for that association and fill in the Item
Property field.

Overall, the context diagram for a coffee machine provides a high-level view of
the system and its interactions with external entities. It is a useful tool for
understanding the system and its role in the broader environment.

## Concept Requirements
Concept requirements are typically collected by analyzing the needs of the
stakeholders involved in the development of the coffee machine. This involves
identifying and gathering input from various stakeholders, such as the barista,
the other engineers working on the product, manufacturing, and service.

To collect concept requirements, stakeholders may be asked questions about what
they want the coffee machine to do, what features it should have, and what
problems it should solve. They may also be asked to provide feedback on
existing coffee machines to identify areas where improvements could be made.

Once the needs of the stakeholders have been gathered, they can be analyzed to
identify common themes and requirements. This information can then be used to
develop the concept requirements for the coffee machine, which serve as a
starting point for the design process.

The following are some concept requirements for a coffee machine that addresses
a water tank, heat-up time, and HMI button:

-  Water Tank: The coffee machine shall have a water tank of sufficient size to
   make multiple cups of coffee before needing a refill. The water tank should be
   easy to access and fill.

-  Heat-up Time: The coffee machine shall have a heat-up time of no more than 10
   minutes from the time the user turns on the machine until it's ready to brew
   coffee.

-  1 Cup Button: The coffee machine shall have an HMI with a 1 cup brew button to
   make it easy for the user to select the amount of coffee they want to brew.

```{diagram} Concept Requirements
:model: coffee-machine
:alt: Concept requirements for water tank, heat-up time, and HMI button
```

Help the ants update the Concept Requirements diagram with these
requirements.

Throughout the design process, the concept requirements will be refined and
expanded upon as more information becomes available and the needs of the
stakeholders become clearer. This iterative process ensures that the final
design of the coffee machine meets the needs of all stakeholders and delivers a
high-quality product.
