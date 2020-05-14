# Services

Gaphor is modeled around the concept of Services. Each service can be
registered with the application and then be used by other services or
other objects living within the application.

Each service should implement the Service interface. This interface
defines one method:

    shutdown(self)

Which is called when a service needs to be cleaned up.

Each service is allowed to define its own interface, as long as Service
is implemented too.

Services should be defined as entry points in the `pyproject.toml` file.

Typically a service does some work in the background. Service can also expose
actions that can be invoked by users. For example, the _Ctrl-z_ key combo
(undo) is implemented by the UndoManager service.

A service can depend on another services. Dependencies are resolved during
service initialization. To define a service dependency, just add it to the
constructor by it's name defined in the entrypoint:

    class MyService(Service):

        def __init__(self, event_manager, element_factory):
            self.event_manager = event_manager
            self.element_factory = element_factory
            event_manager.subscribe(self._element_changed)

        def shutdown(self):
            self.event_manager.unsubscribe(self._element_changed)

        @event_handler(ElementChanged)
        def _element_changed(self, event):

Services that expose actions should also inherit from the ActionProvider
interface. This interface does not require any additional methods to be
implemented. Action methods should be annotated with a `@action` annotation.

## Example: ElementFactory

A nice example of a service in use is the ElementFactory. It is one of the core services.

The UndoManager depends on the events emitted by the ElementFactory. When an
important events occurs, like an element is created or destroyed, that event is
emitted. We then use an event handler for ElementFactory that stores the
add/remove signals in the undo system. Another example of events that are
emitted are with `UML.Element`s. Those classes, or more specifically, the
properties, send notifications every time their state changes.

```eval_rst
.. autoclass:: gaphor.core.modeling.ElementFactory
```
