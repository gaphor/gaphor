import hashlib
from pathlib import Path

from gi.repository import Adw, Gio, GLib, Gtk

from gaphor.abc import ActionProvider
from gaphor.core import event_handler
from gaphor.core.modeling import ModelReady
from gaphor.event import ModelSaved
from gaphor.i18n import translated_ui_string
from gaphor.ui.abc import UIComponent


def new_builder():
    builder = Gtk.Builder()
    builder.add_from_string(translated_ui_string("gaphor.ui", "modelchanged.ui"))
    return builder


def file_digest(filename: Path | None) -> bytes | None:
    if filename is None or not filename.exists():
        return None

    with open(filename, "rb") as f:
        return hashlib.file_digest(f, "sha256").digest()


class ModelChanged(UIComponent, ActionProvider):
    """Show a banner if the current model file has changed.

    This service checks for content changes (file digest)
    to determine if a file really changed.
    """

    def __init__(self, event_manager):
        self.event_manager = event_manager
        self._filename: Path | None = None
        self._file_digest: bytes | None = None
        self._banner: Adw.Banner | None = None
        self._monitor: Gio.FileMonitor | None = None
        self._timeout_id: int = 0
        self.event_manager.subscribe(self._on_model_reset)

    def shutdown(self):
        super().shutdown()
        self.event_manager.unsubscribe(self._on_model_reset)

    def open(self):
        builder = new_builder()
        self._banner = builder.get_object("model-changed")
        self._update_monitor()
        return self._banner

    def close(self):
        self._cancel_monitor()
        self._banner = None

    def _update_monitor(self):
        self._cancel_monitor()
        if self._filename:
            monitor = Gio.File.parse_name(str(self._filename)).monitor(
                Gio.FileMonitorFlags.NONE, None
            )
            monitor.connect("changed", self._on_file_changed)
            self._monitor = monitor

    def _cancel_monitor(self):
        if self._monitor:
            self._monitor.disconnect_by_func(self._on_file_changed)
            self._monitor = None

    def _on_file_changed(self, _monitor, _file, _other_file, event_type):
        if (
            self._timeout_id == 0
            and self._banner
            and event_type != Gio.FileMonitorEvent.ATTRIBUTE_CHANGED
            and self._file_digest != file_digest(self._filename)
        ):
            self._timeout_id = GLib.timeout_add(1000, self._delayed_reveal)

    def _delayed_reveal(self):
        if self._banner:
            self._banner.set_revealed(True)
        self._timeout_id = 0
        return GLib.SOURCE_REMOVE

    @event_handler(ModelReady, ModelSaved)
    def _on_model_reset(self, event: ModelReady | ModelSaved):
        if event.filename != self._filename:
            self._filename = event.filename
            self._update_monitor()

        self._file_digest = file_digest(self._filename)

        if self._timeout_id:
            GLib.source_remove(self._timeout_id)
            self._timeout_id = 0

        if self._banner:
            self._banner.set_revealed(False)
