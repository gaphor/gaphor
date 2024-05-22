from gi.repository import Gtk

from gaphor.abc import ActionProvider
from gaphor.core import event_handler
from gaphor.core.modeling import ModelReady
from gaphor.event import ModelChangedOnDisk, ModelSaved
from gaphor.i18n import translated_ui_string
from gaphor.ui.abc import UIComponent


def new_builder():
    builder = Gtk.Builder()
    builder.add_from_string(translated_ui_string("gaphor.ui", "modelchanged.ui"))
    return builder


class ModelChanged(UIComponent, ActionProvider):
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self._banner = None
        self._monitor = None
        self.event_manager.subscribe(self._on_show_banner)
        self.event_manager.subscribe(self._on_model_reset)

    def shutdown(self):
        super().shutdown()
        self.event_manager.subscribe(self._on_show_banner)
        self.event_manager.unsubscribe(self._on_model_reset)

    def open(self):
        """Open the diagrams component."""
        builder = new_builder()
        self._banner = builder.get_object("model-changed")
        return self._banner

    def close(self):
        """Close the diagrams component."""
        self._banner = None

    @event_handler(ModelChangedOnDisk)
    def _on_show_banner(self, _event):
        if self._banner:
            self._banner.set_revealed(True)

    @event_handler(ModelReady, ModelSaved)
    def _on_model_reset(self, _event):
        if self._banner:
            self._banner.set_revealed(False)
