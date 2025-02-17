# Plugins

```{important}
Plugins is an experimental feature! The API may change.

We welcome you to try and provide your feedback.
```

Plugins allow you to extend the functionality of Gaphor beyond the features provided in the standard distributions.
In particular, plugins can be helpful if you install the binary distributions available on the [download page](https://gaphor.org/download/).

Gaphor can be extended via entry points in several ways:

1. Application (global) services (`gaphor.appservices`)
2. Session specific services (`gaphor.services`)
3. [Modeling languages](modeling_language) (`gaphor.modelinglanguages`)
4. (Sub)command line parsers (`gaphor.argparsers`)
5. Indirectly loaded modules (`gaphor.modules`), mainly for UI components


The default location for plugins is `$HOME/.local/gaphor/plugins-2` (`$USER/.local/gaphor/plugins-2` on Windows).
This location can be changed by setting the environment variable `GAPHOR_PLUGIN_PATH` and point to a directory.


## Install a plugin

At this moment Gaphor does not have functionality bundled to install and maintain plugins.
To install a plugin, use `pip` from a Python installation on your computer. On macOS and Linux, that should be easy,
on Windows you may need to install Python separately from [python.org](https://python.org) or the Windows Store.

```{important}
1. Since plugins are installed with your system Python version, it's important that plugins are pure Python and do
   not contain compiled C code.
1. If you use Gaphor installed as Flatpak, you need to grant Gaphor access to user files
   (`filesystem=home`), so Gaphor can find files in your `.local` folder. You can use
   [FlatSeal](https://flathub.org/apps/com.github.tchx84.Flatseal) to change permissions of Flatpaks.
```

For example: to install the [Hello World plugin](https://github.com/gaphor/gaphor_plugin_helloworld) on Linux and macOS, enter:

```bash
pip install --target $HOME/.local/gaphor/plugins-2 git+https://github.com/gaphor/gaphor_plugin_helloworld.git
```

Then start Gaphor as you normally would.
A new Hello World entry has been added to the tools menu (![Menu icon](images/open-menu-symbolic.svg) → Tools → Hello World).

## Create your own plugin

If you want to write a plugin yourself, you can familiarize yourself with Gaphor's
[design principles](design_principles), [service oriented architecture](service_oriented),
and [event driven framework](framework).

## Example plugin

You can have a look at the [Hello World plugin](https://github.com/gaphor/gaphor_plugin_helloworld) available on GitHub for an example of how to create your own plugin.

The
[pyproject.toml](https://github.com/gaphor/gaphor_plugin_helloworld/blob/main/pyproject.toml)
file contains a plugin:

```yaml
[tool.poetry.plugins."gaphor.services"]
"helloworld" = "gaphor_helloworld_plugin:HelloWorldPlugin"
```

This refers to the class `HelloWorldPlugin` in package/module
[gaphor_plugins_helloworld](https://github.com/gaphor/gaphor_plugin_helloworld/blob/main/gaphor_helloworld_plugin/__init__.py).

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

    @action(                                         # 5.
        name="helloworld",
        label=_("Hello world"),
        tooltip=_("Every application…"),
    )
    def helloworld_action(self):
        main_window = self.main_window
        ...  # gtk code left out
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

## Plugin Development FAQ

### How do I acceess gaphor services in my plugin?

Gaphor's services can be made accessible by listing the service names in the init function of your plugin class. This
also requires including Service as a base class. In the HelloWorldPlugin example, the tools_menu service is included.

A more complete description of this approach can be found in the [Service Oriented Architecture documentation
page](service_oriented.md).

## Community Developed Plugins

### Gaphor_Tools
#### What does it do?
Import and export of SysML requirements and notes to Excel and Confluence. It's currently at the proof-of-concept stage of development, but does allow a requirements table to be exported, then edited and imported bringing in all the changes to the model, similarly for element notes.
#### Where can I get it?
From this [BitBucket Repo](https://bitbucket.org/resonatesystems/gaphor_tools/src/main/)
