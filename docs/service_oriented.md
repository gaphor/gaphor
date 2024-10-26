# Service Oriented Architecture

Gaphor has a service oriented architecture. What does this mean? Well, Gaphor
is built as a set of small islands (services). Each island provides a specific
piece of functionality. For example, we use separate services to load/save
models, provide the menu structure, and to handle the undo system.

We define services as entry points in the `pyproject.toml`. With entry points,
applications can register functionality for specific purposes. We also group
entry points in to *entry point groups*. For example, we use the
console_scripts entry point group to start an application from the command
line.


## Services

Gaphor is modeled around the concept of services. Each service can be
registered with the application and then it can be used by other services or
other objects living within the application.

Each service should implement the Service interface. This interface
defines one method:

```{code-block} python
shutdown(self)
```

Which is called when a service needs to be cleaned up.

We allow each service to define its own methods, as long as the service
is implemented too.

Services should be defined as entry points in the `pyproject.toml` file.

Typically, a service does some work in the background. Services can also expose
actions that can be invoked by users. For example, the _Ctrl-z_ key combo
(undo) is implemented by the UndoManager service.

A service can also depend on another services. Service initialization resolves
these dependencies. To define a service dependency, just add it to the
constructor by its name defined in the entry point:

```{code-block} python
class MyService(Service):

    def __init__(self, event_manager, element_factory):
        self.event_manager = event_manager
        self.element_factory = element_factory
        event_manager.subscribe(self._element_changed)

    def shutdown(self):
        self.event_manager.unsubscribe(self._element_changed)

    @event_handler(ElementChanged)
    def _element_changed(self, event):
```

Services that expose actions should also inherit from the ActionProvider
interface. This interface does not require any additional methods to be
implemented. Action methods should be annotated with an `@action` annotation.

## Example: ElementFactory

A nice example of a service in use is the
{obj}`~gaphor.core.modeling.ElementFactory`. It is one of the core services.

When an
important events occurs, like an element is created or destroyed, that event is
emitted. We then use an event handler for `ElementFactory` that stores the
add/remove signals in the undo system. Another example of events that are
emitted are with {obj}`~gaphor.core.modeling.Element`'s. Those classes, or more specifically, the
properties, send notifications every time their state changes.

## Entry Points

Gaphor uses a main :ref`entry point <https://packaging.python.org/en/latest/specifications/entry-points/>` group called `gaphor.services`.

Services are used to perform the core functionality of the application while
breaking the functions in to individual components. For example, the element
factory and undo manager are both services.

Plugins can also be created to extend Gaphor beyond the core functionality as
an add-on. For example, a plugin could be created to connect model data to
other applications. Plugins are also defined as services. For example a new XMI
export plugin would be defined as follows in the `pyproject.toml`:

```toml
[tool.poetry.plugins."gaphor.services"]
"xmi_export" = "gaphor.plugins.xmiexport:XMIExport"
```

## Interfaces

Each service (and plugin) should implement the `gaphor.abc.Service` interface:

```{eval-rst}
.. autoclass:: gaphor.abc.Service
   :members:
```

Another more specialized service that also inherits from `gaphor.abc.Service`,
is the UI Component service. Services that use this interface are used to
define windows and user interface functionality. A UI component should
implement the `gaphor.ui.abc.UIComponent` interface:

```{eval-rst}
.. autoclass:: gaphor.ui.abc.UIComponent
   :members:
```

Typically, a service and UI component would like to present some actions
to the user, by means of menu entries. Every service and UI component
can advertise actions by implementing the `gaphor.abc.ActionProvider`
interface:

```{eval-rst}
.. autoclass:: gaphor.abc.ActionProvider
   :members:
```
