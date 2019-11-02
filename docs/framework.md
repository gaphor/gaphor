# Gaphor's Framework

## Overview

Gaphor is built in a light, service oriented fashion. The application is
split in a series of services, such as a file manager, undo manager and GUI
manager. Those services are loaded based on entry points defined in the
`pyproject.toml` file. To learn more about the architecture, please see the
description about the [Service Oriented Architecture](so.md)).

## Events

Parts of Gaphor communicate with each other through events. Whenever
something import happens, for example an attribute of a model element
changes, an event is sent. When other parts of the application are interested
in a change, they register an event handler for that event type. Events are
emitted though a central broker so you do not have to register on every
individual element that can send an event they are interested in. For
example, a diagram item could register an event rule and then check if the
element that sent the event is actually the event the item is representing.

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
services defined as [gaphor.services](services.md). Those services are loaded
and initialized.

The most notable services are:

### file_manager

Loading and saving a model is done through this service.

### element_factory

The [data model](datamodel.md) itself is maintained in the element factory
(`gaphor.UML.elementfactory`). This service is used to create model elements,
as well as to lookup elements or query for a set of elements.

### [undo_manager](undo.md)

One of the most appreciated services. It allows users to make a mistake every
now and then!

The undo manager is transactional. Actions performed by a user are
only stored if a transaction is active. If a transaction is
completed (committed) a new undo action is stored. Transactions can
also be rolled back, in which case all changes are played back
directly.

### element_dispatcher

Although Gaphor makes use of a central dispatch engine, this
solution is not efficient when it comes to dispatching events of UML
model elements. For this purpose the `element_dispatcher` can help
out. It maintains a path of elements from the root item, for example a
diagram item to the element of interest. A signal will only be sent
in case the root item changes. This makes complex dispatching very
efficient. The dispatcher functionality is available through
Element.watcher().

```eval_rst
.. autoclass:: gaphor.UML.elementdispatcher.ElementDispatcher
```
