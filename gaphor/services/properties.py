"""The properties module allows Gaphor properties to be saved to the local file
system.

These are things like preferences.
"""


import ast
import logging
import pprint
from pathlib import Path
from typing import Dict

from gaphor import settings
from gaphor.abc import Service
from gaphor.core import event_handler
from gaphor.core.modeling.event import ModelFlushed
from gaphor.event import ModelSaved, SessionCreated

log = logging.getLogger(__name__)


def properties_filename(filename: str) -> Path:
    return settings.get_cache_dir() / settings.file_hash(filename)


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
        self.filename: Path = properties_filename("")
        self._properties: Dict[str, object] = {}

        event_manager.subscribe(self.on_model_loaded)
        event_manager.subscribe(self.on_model_saved)
        event_manager.subscribe(self.on_model_flushed)

    def shutdown(self):
        """Shutdown the properties service.

        This will ensure that all properties are saved.
        """
        self.save()

        self.event_manager.unsubscribe(self.on_model_loaded)
        self.event_manager.unsubscribe(self.on_model_saved)
        self.event_manager.unsubscribe(self.on_model_flushed)

    @event_handler(SessionCreated)
    def on_model_loaded(self, event):
        self.filename = properties_filename(event.filename or "")
        self.load()

    @event_handler(ModelSaved)
    def on_model_saved(self, event):
        self.filename = properties_filename(event.filename)
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

        if filename.is_file():
            data = filename.read_text(encoding="utf-8")
            try:
                self._properties = ast.literal_eval(data)
            except SyntaxError:
                log.error(f"Invalid syntax in property file {filename}")

            for key, value in list(self._properties.items()):
                self.event_manager.handle(PropertyChanged(key, None, value))

    def save(self):
        """Save all properties by calling save() on the properties storage
        backend."""

        if not self.filename:
            return

        with open(self.filename, "w", encoding="utf-8") as ofile:
            pprint.pprint(self._properties, ofile)  # noqa: T203

    def get(self, key: str, default=_no_default):
        """Locate a property.

        Resource should be the class of the resource to look for or a
        string. In case of a string the resource will be looked up in
        the GConf configuration.
        """

        try:
            return self._properties[key]
        except KeyError as e:
            if default is _no_default:
                raise KeyError(f'No resource with name "{key}"') from e

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
