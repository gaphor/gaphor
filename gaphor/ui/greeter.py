from gi.repository import Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.action import action
from gaphor.core import event_handler
from gaphor.event import SessionCreated
from gaphor.i18n import translated_ui_string


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
        self.recent_files = [
            ("UML.gaphor", "~/Development/gaphor/models"),
            ("Core.gaphor", "~/Development/gaphor/models"),
            ("Fables.gaphor", "~/a-different-folder"),
            ("FooBar.gaphor", "~/a-different-folder"),
            ("Fifth Entry.gaphor", "~/a-different-folder"),
        ]
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

        greeter.show()
        self.greeter = greeter

    @action(name="app.new-model")
    def new_model(self):
        self.application.new_session()

    def create_recent_files(self):
        for filename, folder in self.recent_files:
            builder = new_builder("greeter-recent-file")
            builder.get_object("filename").set_text(filename)
            builder.get_object("folder").set_text(folder)
            yield builder.get_object("greeter-recent-file")

    @event_handler(SessionCreated)
    def on_session_created(self, event):
        if self.greeter:
            self.greeter.destroy()
            self.greeter = None
