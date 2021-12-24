from pathlib import Path

from gi.repository import GLib, Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.action import action
from gaphor.core import event_handler
from gaphor.event import SessionCreated
from gaphor.i18n import translated_ui_string
from gaphor.ui import APPLICATION_ID, HOME


def new_builder(ui_file):
    builder = Gtk.Builder()
    ui_file = f"{ui_file}.glade" if Gtk.get_major_version() == 3 else f"{ui_file}.ui"
    builder.add_from_string(translated_ui_string("gaphor.ui", ui_file))
    return builder


class Greeter(Service, ActionProvider):
    def __init__(self, application, event_manager):
        self.application = application
        self.event_manager = event_manager
        self.greeter = None
        self.gtk_app = None
        event_manager.subscribe(self.on_session_created)

    def init(self, gtk_app):
        self.gtk_app = gtk_app

    def shutdown(self):
        self.event_manager.unsubscribe(self.on_session_created)
        if self.greeter:
            self.greeter.destroy()
        self.gtk_app = None

    @action(name="app.new", shortcut="<Primary>n")
    def new(self):
        builder = new_builder("greeter")
        greeter = builder.get_object("greeter")
        greeter.set_application(self.gtk_app)

        listbox = builder.get_object("greeter-recent-files")
        for widget in self.create_recent_files():
            listbox.add(widget)

        listbox.connect("row-activated", self._on_row_activated)
        greeter.show()
        self.greeter = greeter

    @action(name="app.new-model")
    def new_model(self):
        self.application.new_session()

    def create_recent_files(self):
        recent_manager = Gtk.RecentManager.get_default()

        for item in recent_manager.get_items():
            if APPLICATION_ID in item.get_applications() and item.exists():
                builder = new_builder("greeter-recent-file")
                filename, _host = GLib.filename_from_uri(item.get_uri())
                builder.get_object("name").set_text(str(Path(filename).stem))
                builder.get_object("filename").set_text(
                    item.get_uri_display().replace(HOME, "~")
                )
                row = builder.get_object("greeter-recent-file")
                row.filename = filename
                yield row

    @event_handler(SessionCreated)
    def on_session_created(self, _event=None):
        if self.greeter:
            self.greeter.destroy()
            self.greeter = None

    def _on_row_activated(self, _listbox, row):
        filename = row.filename
        self.application.new_session(filename=filename)
        # Always close the greeter: we may just focus another window
        self.on_session_created()
