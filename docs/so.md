# Service Oriented Architecture

Gaphor has a service oriented architecture. What does this mean? Well, Gaphor
is built as a set of small islands (services). Each island provides a specific
piece of functionality. For example, separate services are used to load/save
models, provide the menu structure, and handle the undo system.

Service are defined as entry points in the `pyproject.toml`. With entry points
applications can register functionality for specific purposes. Entry points are
grouped in so called *entry point groups*. For example the console_scripts
entry point group is used to start an application from the command line.

Entry Points
============

Gaphor uses a main entry point group called `gaphor.services`.

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

```eval_rst
.. autoclass:: gaphor.abc.Service
```

Another more specialized service that also inherits from `gaphor.abc.Service`,
is the UI Component service. Services that use this interface are used to
define windows and user interface functionality. A UI component should
implement the `gaphor.ui.abc.UIComponent` interface:

```eval_rst
.. autoclass:: gaphor.ui.abc.UIComponent
```

Typically a service and UI component would like to present some actions
to the user, by means of menu entries. Every service and UI component
can advertise actions by implementing the `gaphor.abc.ActionProvider`
interface:

```eval_rst
.. autoclass:: gaphor.abc.ActionProvider 
```

## Example plugin

A small example is provided by means of the Hello world plugin. Take a look at
the files at [GitHub](https://github.com/gaphor/gaphor.plugins.helloworld). The
example plugin needs to be updated to support versions 1.0.0 and later of Gaphor.

The
[setup.py](https://github.com/gaphor/gaphor.plugins.helloworld/blob/master/setup.py)
file contains an entry point:

    entry_points = {
        'gaphor.services': [
            'helloworld = gaphor.plugins.helloworld:HelloWorldPlugin',
        ]
    }

This refers to the class `HelloWorldPlugin` in package/module
[gaphor.plugins.helloworld](https://github.com/gaphor/gaphor.plugins.helloworld/blob/master/gaphor/plugins/helloworld/__init__.py).

Here is a stripped version of the hello world plugin:

```python
from gaphor.abc import Service, ActionProvider
from gaphor.core import _, action

class HelloWorldPlugin(Service, ActionProvider):     # 1.

    def __init__(self, tools_menu):                  # 2.
        self.tools_menu = tools_menu
        tools_menu.add_actions(self)                 # 3.

    def shutdown(self):                              # 4.
        self.tools_menu.remove_actions(self)

    @action(name='helloworld',                       # 5.
            label=_('Hello world'),
            tooltip=_('Every application ...'))
    def helloworld_action(self):
        main_window = self.main_window
        pass # gtk code left out
```

1.  As stated before, a plugin should implement the `Service` interface.
    It also implements `ActionProvider`, saying it has some actions to
    be performed by the user.
2.  The menu entry will be part of the "Tools" extension menu. This
    extension point is created as a service. Other services can also be
    passed as dependencies. Services can get references to other
    services by defining them as arguments of the constructor.
3.  All action defined in this service are registered.
4.  Each service has a `shutdown()` method. This allows the service to
    perform some cleanup when it's shut down.
5.  The action that can be invoked. The action is defined and will be
    picked up by `add_actions()` method (see 3.)
