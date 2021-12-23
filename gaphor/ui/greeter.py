from gi.repository import Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.action import action
from gaphor.i18n import translated_ui_string


def new_builder(ui_file):
    builder = Gtk.Builder()
    ui_file = f"{ui_file}.glade" if Gtk.get_major_version() == 3 else f"{ui_file}.ui"
    builder.add_from_string(translated_ui_string("gaphor.ui", ui_file))
    return builder


class Greeter(Service, ActionProvider):
    def __init__(self, application):
        self.application = application
        self.recent_files = [
            ("UML.gaphor", "~/Development/gaphor/models"),
            ("Core.gaphor", "~/Development/gaphor/models"),
        ]

    @action(name="app.new", shortcut="<Primary>n")
    def action_new(self):
        """The new model menu action.

        This action will create a new UML model.  This will trigger a
        FileManagerStateChange event.
        """
        builder = new_builder("greeter")
        greeter = builder.get_object("greeter")

        listbox = builder.get_object("greeter-recent-files")
        for widget in self.create_recent_files():
            listbox.add(widget)

        greeter.show()

        # noqa E800 self.application.new_session()

    def create_recent_files(self):
        for filename, folder in self.recent_files:
            builder = new_builder("greeter-recent-file")
            builder.get_object("filename").set_text(filename)
            builder.get_object("folder").set_text(folder)
            yield builder.get_object("greeter-recent-file")

    def shutdown(self):
        pass


if __name__ == "__main__":
    application = None
    greeter = Greeter(application)

    greeter.action_new()

    Gtk.main()
