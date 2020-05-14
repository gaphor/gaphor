# Framework

## Overview

Gaphor is built in a light, service oriented fashion. The application is split
in a series of services, such as a file, event, and undo managers. Those
services are loaded based on entry points defined in the `pyproject.toml` file.
To learn more about the architecture, please see the description about the
[Service Oriented Architecture](service_oriented.md).

## Events

Parts of Gaphor communicate with each other through events. Whenever something
important happens, for example, an attribute of a model element changes, an
event is sent. When other parts of the application are interested in a change,
they register an event handler for that event type. Events are emitted though a
central broker so you do not have to register on every individual element that
can send an event they are interested in. For example, a diagram item could
register an event rule and then check if the element that sent the event is
actually the event the item is representing. For more information see the full
description of the [event system](event_system.md).

## Transactional

Gaphor is transactional, which means it keeps track of the functions it
performs as a series of transactions. The transactions work by sending an
event when a transaction starts and sending another when a transaction ends.
This allows, for example, the undo manager to keep a running log of the
previous transactions so that a transaction can be reversed if the undo
button is pressed.

## Main Components

The main portion of Gaphor that executes first is called the `Application`.
Only one Application instance is permitted. The Application will look for
services defined as [gaphor.services](service_oriented.md). Those services are loaded
and initialized.

The most notable services are:

### event_manager

This is the central compoment used for event dispatching. Every service that
does something with events (both sending and receiving) depends on this
component.

### file_manager

Loading and saving a model is done through this service.

### element_factory

The [data model](datamodel.md) itself is maintained in the element factory
(`gaphor.UML.elementfactory`). This service is used to create model elements,
as well as to lookup elements or query for a set of elements.

### undo_manager

One of the most appreciated services. It allows users to make a mistake every
now and then!

The undo manager is transactional. Actions performed by a user are only stored
if a transaction is active. If a transaction is completed (committed) a new
undo action is stored. Transactions can also be rolled back, in which case all
changes are played back directly. For more information see the full description
of the [undo manager](undo.md)
