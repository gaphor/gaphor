# Services

Gaphor is modeled around the concept of Services. Each service can be
registered with the application and then be used by other services or
other objects living within the application.

Each service should implement the Service interface. This interface
defines one method:

    init(application)

where application is the Application object for Gaphor (which is a
service itself and therefore implements Service too.

Each service is allowed to define its own interface, as long as Service
is implemented too.

Services should be defined as entry_points in the `pyproject.toml` file.

Typically a service does some work in the background.

## Example: ElementFactory

A nice example of a service in use is the ElementFactory. Currently it is
tightly bound to the `gaphor.UML` module. A default factory is created in
`__init__.py`.

The undo_manager depends on the events emitted by the ElementFactory. When an
important events occurs, like an element is created or destroyed, that event is
emitted. We then use an event handler for ElementFactory that stores the
add/remove signals in the undo system. Another example of events that are
emitted are with `UML.Elements`. Those classes, or more specifically, the
properties, send notifications every time their state changes.

```eval_rst
.. autoclass:: gaphor.core.modeling.ElementFactory
```

## Plugins

Currently a plugin is defined by an XML file. This will change as
plugins should be distributable as Eggs too. A plugin will contain user
interface information along with its service definition.

For more information, please also see our how-to on [writing a
plugin](https://gaphor.org/pages/writing-a-plugin.html)
