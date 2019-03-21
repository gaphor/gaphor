Services
========

Gaphor is modeled around the concept of Services. Each service can
be registered with the application and then be used by other services or other
objects living within the application.

Since Gaphor already uses the `zope.component` adapters, it seems like a good
choice to use `zope.interface` too as starting point for services.

Each service should implement the IService interface. This interface defines
one method::

   init(application)

where `application` is the Application object for Gaphor (which is a service
itself and therefore implements `IService` too.

Each service is allowed to define its own interface, as long as `IService` is
implemented too.

Services should be defined as `entry_points` in the Egg info file.

Typically a service does some work in the background.


Example: ElementFactory
***********************

A nice example is the ElementFactory. Currently it is tightly bound to the
gaphor.UML module. A default factory is created in __init__.py.

It depends on the undo_manager. However, on important events, events are emitted.
(That is when an element is created/destroyed).

What you want to do is create an event handler for ElementFactory that stores 
the add/remove signals in the undo system.

The same goes for UML.Elements. Those classes (or more specific the properties)
send notifications every time their state changes.

But.. where to put such information?

.. autoclass:: gaphor.UML.elementfactory.ElementFactory
   :members:

Plugins
=======

Currently a plugin is defined by an XML file. This will change as plugins
should be distributable as Eggs too. A plugin will contain user interface
information along with its service definition.

.. seealso:: 

    :doc:`Writing plugins <manual/plugins>`

