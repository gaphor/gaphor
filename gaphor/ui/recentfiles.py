import os
from pathlib import Path

from gi.repository import Gio, GLib, Gtk

from gaphor.abc import Service
from gaphor.core import event_handler, gettext
from gaphor.ui import APPLICATION_ID
from gaphor.ui.event import FileLoaded, FileSaved

HOME = str(Path.home())


class RecentFiles(Service):
    def __init__(self, event_manager, recent_manager=None):
        self.event_manager = event_manager
        self.recent_manager = recent_manager or Gtk.RecentManager.get_default()

        self.event_manager.subscribe(self._on_filename_changed)

    def shutdown(self):
        self.event_manager.unsubscribe(self._on_filename_changed)

    @event_handler(FileLoaded, FileSaved)
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


class RecentFilesMenu(Gio.Menu):
    def __init__(self, recent_manager):
        super().__init__()

        self._on_recent_manager_changed(recent_manager)
        # TODO: should unregister if the window is closed.
        self._changed_id = recent_manager.connect(
            "changed", self._on_recent_manager_changed
        )

    def _on_recent_manager_changed(self, recent_manager):
        self.remove_all()
        for item in recent_manager.get_items():
            if APPLICATION_ID in item.get_applications():
                menu_item = Gio.MenuItem.new(
                    item.get_uri_display().replace(HOME, "~"), "win.file-open-recent"
                )
                filename, _host = GLib.filename_from_uri(item.get_uri())
                menu_item.set_attribute_value(
                    "target", GLib.Variant.new_string(filename)
                )
                self.append_item(menu_item)
                if self.get_n_items() > 9:
                    break
        if self.get_n_items() == 0:
            self.append_item(
                Gio.MenuItem.new(gettext("No recently opened models"), None)
            )
