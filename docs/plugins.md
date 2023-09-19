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
Since plugins are installed with your system Python version, it's important that
plugins are pure python - e.i. do not contain compiled C code.
```

For example: to install the [Hello World plugin](https://github.com/gaphor/gaphor_plugin_helloworld) on Linux and macOS, enter:

```bash
pip install --target $HOME/.local/gaphor/plugins-2 git+https://github.com/gaphor/gaphor_plugin_helloworld.git
```

Then start Gaphor as you normally would.
A new Hello World entry has been added to the tools menu (![open menu](images/open-menu-symbolic.svg) → Tools → Hello World).

## Create your own plugin

If you want to write a plugin yourself, you can familiarize yourself with Gaphor's
[design principles](design_principles), [service oriented architecture](service_oriented) (includes a plugin example),
and [event driven framework](framework).
Next you can have a look at the [Hello World plugin](https://github.com/gaphor/gaphor_plugin_helloworld) available on GitHub.
