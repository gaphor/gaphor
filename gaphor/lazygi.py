"""This module provides a little wrapper around the Gtk, and UI related
modules.

This basically allows you to import Gaphor modules
without Gtk, which is very convenient in notebooks
and CI environments.

It's remotely related to https://peps.python.org/pep-0690/.

`importlib.util.LazyLoader` does not work, since `gi.repository`
modules are already dynamically loaded.
"""

import importlib
from typing import Any

import gi


class LazyGIModule:
    def __init__(self, gi_name):
        self._gi_name = gi_name
        self._module = None

    def __getattr__(self, name):
        if not gi.get_required_version(self._gi_name):
            raise ImportError(f"No required version set for {self._gi_name}")
        if not self._module:
            self._module = importlib.import_module(f"gi.repository.{self._gi_name}")
        return getattr(self._module, name)


Gdk: Any = LazyGIModule("Gdk")  # type: ignore[misc]
Gtk: Any = LazyGIModule("Gtk")  # type: ignore[misc]
