Event System
============

The event system in Gaphor provides an
API to *handle* events and to *subscribe* to events.

In Gaphor we manage event handler subscriptions through the `EventManager`
service. Gaphor is highly event driven:

* Changes in the loaded model are emitted as events
* Changes on diagrams are emitted as events
* Changes in the UI are emitted as events

Although Gaphor depends heavily on GTK for its user interface, Gaphor is using
its own event dispatcher. Events can be structured in hierarchies. For example,
an `AttributeUpdated` event is a subtype of `ElementUpdated`. If we are interested
in all changes to elements, we can also register `ElementUpdated` and receive all
`AttributeUpdated` events as well.

.. autoclass:: gaphor.core.eventmanager.EventManager

   .. autoclass:: gaphor.core.eventmanager.EventManager.subscribe

   .. autoclass:: gaphor.core.eventmanager.EventManager.unsubscribe

   .. autoclass:: gaphor.core.eventmanager.EventManager.handle

.. autofunction:: gaphor.core.event_handler

Under the hood events are handled by the Generics library.
For more information about how the Generic library handles events see the
`Generic documentation <https://generic.readthedocs.io>`_.
