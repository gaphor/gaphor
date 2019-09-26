import os
from gi.repository import GLib, Gtk

from gaphor.abc import Service
from gaphor.core import event_handler
from gaphor.ui import APPLICATION_ID
from gaphor.ui.event import FilenameChanged


class RecentFiles(Service):
    def __init__(self, event_manager, recent_manager=None):
        print("Recent files initated")
        self.event_manager = event_manager
        self.recent_manager = recent_manager or Gtk.RecentManager.get_default()

        self.event_manager.subscribe(self._on_filename_changed)

    def shutdown(self):
        self.event_manager.unsubscribe(self._on_filename_changed)

    @event_handler(FilenameChanged)
    def _on_filename_changed(self, event):
        filename = event.filename
        if not filename:
            return
        uri = GLib.filename_to_uri(os.path.abspath(filename))
        meta = Gtk.RecentData()
        meta.app_name = APPLICATION_ID
        meta.app_exec = f"{GLib.get_prgname()} %u"
        meta.mime_type = "application/x-gaphor"
        self.recent_manager.add_full(uri, meta)
