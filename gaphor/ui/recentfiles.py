from pathlib import Path

from gi.repository import GLib, Gtk

from gaphor.abc import Service
from gaphor.core import event_handler
from gaphor.event import ModelLoaded, ModelSaved
from gaphor.ui import APPLICATION_ID


class RecentFiles(Service):
    def __init__(self, event_manager, recent_manager=None):
        self.event_manager = event_manager
        self.recent_manager = recent_manager or Gtk.RecentManager.get_default()

        self.event_manager.subscribe(self._on_filename_changed)

    def shutdown(self):
        self.event_manager.unsubscribe(self._on_filename_changed)

    @event_handler(ModelLoaded, ModelSaved)
    def _on_filename_changed(self, event):
        filename = event.filename
        if not filename:
            return
        uri = GLib.filename_to_uri(str(Path(filename).absolute()))
        # Re-add, to ensure it's at the top of the list
        self.remove(uri)
        self.add(uri)

    def add(self, uri):
        meta = Gtk.RecentData()
        meta.app_name = APPLICATION_ID
        meta.app_exec = f"{GLib.get_prgname()} %u"
        meta.mime_type = "application/x-gaphor"
        self.recent_manager.add_full(uri, meta)

    def remove(self, uri):
        # From: https://gitlab.gnome.org/GNOME/pitivi/-/blob/58b5e3b6/pitivi/application.py#L271
        try:
            self.recent_manager.remove_item(uri)
        except GLib.Error as e:
            if e.domain != "gtk-recent-manager-error-quark":
                raise e
