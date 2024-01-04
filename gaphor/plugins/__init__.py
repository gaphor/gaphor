"""
Plugins
=======

This module contains a bunch of standard plugins.
Plugins can be registered in Gaphor by declaring them as service entry point::

    entry_points = {
        'gaphor.services': [
            'xmi_export = gaphor.plugins.xmiexport:XMIExport',
        ],
    },


There is a thin line between a service and a plugin. A service typically performs some basic need for the applications (such as the element factory or the undo mechanism). A plugin is more of an add-on. For example a plugin can depend on external libraries or provide a cross-over function between two applications.

"""
import contextlib
import importlib.abc
import importlib.machinery
import importlib.metadata
import os
import pathlib
import sys

from gaphor import entrypoint

PLUGIN_VERSION = 2


def default_plugin_path() -> pathlib.Path:
    if plugin_path_envvar := os.getenv("GAPHOR_PLUGIN_PATH"):
        return pathlib.Path(plugin_path_envvar)
    return pathlib.Path.home() / ".local" / "gaphor" / f"plugins-{PLUGIN_VERSION}"


@contextlib.contextmanager
def enable_plugins(plugin_path: pathlib.Path):
    entrypoint.list_entry_points.cache_clear()
    path_finder = PluginMetaPathFinder(plugin_path)
    sys.meta_path.append(path_finder)
    yield
    sys.meta_path.remove(path_finder)


class PluginMetaPathFinder(importlib.abc.MetaPathFinder):
    def __init__(self, plugin_path: pathlib.Path):
        self.plugin_path = str(plugin_path)

    def find_spec(self, fullname, path=None, target=None):
        return importlib.machinery.PathFinder.find_spec(
            fullname, path=[self.plugin_path], target=target
        )

    def find_distributions(self, *args, **kwargs):
        return importlib.metadata.MetadataPathFinder.find_distributions(
            context=importlib.metadata.DistributionFinder.Context(
                path=[self.plugin_path]
            )
        )
