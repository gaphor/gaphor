"""The properties module allows Gaphor properties to be saved to the local file
system.

These are things like preferences.
"""

import ast
import hashlib
import os
import pprint
from typing import Dict

from gi.repository import GLib

from gaphor.abc import Service
from gaphor.core import event_handler
from gaphor.core.modeling.event import ModelFlushed
from gaphor.event import ModelLoaded, ModelSaved, SessionCreated


def get_config_dir() -> str:
    """Return the directory where the user's config is stored.

    This varies depending on platform.
    """

    config_dir = os.path.join(GLib.get_user_config_dir(), "gaphor")
    os.makedirs(config_dir, exist_ok=True)

    return config_dir


def get_cache_dir() -> str:
    """Return the directory where the user's cache is stored.

    This varies depending on platform.
    """

    cache_dir = os.path.join(GLib.get_user_cache_dir(), "gaphor")
    os.makedirs(cache_dir, exist_ok=True)

    return cache_dir


def file_hash(filename: str) -> str:
    return hashlib.blake2b(str(filename).encode("utf-8"), digest_size=24).hexdigest()


class PropertyChanged:
    """This event is triggered any time a property is changed.

    This event holds the property key, the current value, and the new
    value.
    """

    def __init__(self, key, old_value, new_value):
        self.key = key
        self.old_value = old_value
        self.new_value = new_value


_no_default = object()


class Properties(Service):
    """The Properties class holds a collection of application wide properties.

    Properties are persisted to the local file system.
    """

    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.filename = os.path.join(get_cache_dir(), file_hash(""))
        self._properties: Dict[str, object] = {}

        event_manager.subscribe(self.on_model_loaded)
        event_manager.subscribe(self.on_model_saved)
        event_manager.subscribe(self.on_model_flushed)

        self.load()

    def shutdown(self):
        """Shutdown the properties service.

        This will ensure that all properties are saved.
        """
        self.save()

        self.event_manager.unsubscribe(self.on_model_loaded)
        self.event_manager.unsubscribe(self.on_model_saved)
        self.event_manager.unsubscribe(self.on_model_flushed)

    @event_handler(ModelLoaded, SessionCreated)
    def on_model_loaded(self, event):
        self.filename = os.path.join(get_cache_dir(), file_hash(event.filename or ""))
        self.load()

    @event_handler(ModelSaved)
    def on_model_saved(self, event):
        self.filename = os.path.join(get_cache_dir(), file_hash(event.filename))
        self.save()

    @event_handler(ModelFlushed)
    def on_model_flushed(self, event):
        if self.filename:
            self.save()

    def __call__(self, key, default=_no_default):
        """Retrieve the specified property.

        If the property doesn't exist, the default parameter is
        returned.  This defaults to _no_default.
        """

        return self.get(key, default)

    def load(self):
        """Load properties from a file.

        Resources are loaded like you do with a dict().
        """

        filename = self.filename

        if os.path.exists(filename) and os.path.isfile(filename):

            with open(filename) as ifile:
                data = ifile.read()

            self._properties = ast.literal_eval(data)
            for key, value in list(self._properties.items()):
                self.event_manager.handle(PropertyChanged(key, None, value))

    def save(self):
        """Save all properties by calling save() on the properties storage
        backend."""

        if not self.filename:
            return

        with open(self.filename, "w") as ofile:
            pprint.pprint(self._properties, ofile)

    def get(self, key: str, default=_no_default):
        """Locate a property.

        Resource should be the class of the resource to look for or a
        string. In case of a string the resource will be looked up in
        the GConf configuration.
        """

        try:
            return self._properties[key]
        except KeyError:
            if default is _no_default:
                raise KeyError(f'No resource with name "{key}"')

            self.set(key, default)
            return default

    def set(self, key, value):
        """Set a property to a specific value.

        No smart things are done with classes and class names (like the
        resource() method does).
        """

        properties = self._properties
        old_value = properties.get(key)

        if value != old_value:
            properties[key] = value
            self.event_manager.handle(PropertyChanged(key, old_value, value))
