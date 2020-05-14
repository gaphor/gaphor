# Event System

The Generic library provides the `generic.event` module which is used to
implement the event system in Gaphor. This event system in Gaphor provides an
API to *subscribe* to events and to then *handle* those events so previously
subscribed *handlers* are being executed.

In Gaphor event handler subscribtions are managed through the EventManager service. Gaphor is highly event driven:

 * Changes in the loaded model are emitted as events
 * Changes on diagrams are emitted as events
 * Changes in the UI are emitted as events

Although Gaphor depends heavily on GTK got it's user interface, Gaphor is using
it's own event dispatcher. Events can be structured in hierarchies. For
example: an AttributeUpdated event is a subtype of ElementUpdated. If I'm
interested in all changes done to elements I can register to ElementUpdated and
recieve all AttributeUpdated events as well.

```eval_rst
.. autoclass:: gaphor.core.eventmanager.EventManager
   :members:
```

For more information about how the Generic library handles events see the
[Generic documentation](https://generic.readthedocs.io).
