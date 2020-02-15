"""About and help services. (help browser anyone?)"""


import importlib

import importlib_metadata
from gi.repository import GdkPixbuf, Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.core import action


class HelpService(Service, ActionProvider):
    def __init__(self, session):
        self.session = session

    def shutdown(self):
        pass

    @property
    def window(self):
        return self.session.get_service("main_window").window

    @action(name="app.about")
    def about(self):
        builder = Gtk.Builder()
        with importlib.resources.path(
            "gaphor.services.helpservice", "about.glade"
        ) as glade_file:
            builder.add_objects_from_file(str(glade_file), ("about",))

        about = builder.get_object("about")

        about.set_version(importlib_metadata.version("gaphor"))

        about.set_transient_for(self.window)

        about.show_all()
        about.run()
        about.destroy()

    @action(name="app.shortcuts")
    def shortcuts(self):
        builder = Gtk.Builder()
        with importlib.resources.path(
            "gaphor.services.helpservice", "shortcuts.glade"
        ) as glade_file:
            builder.add_objects_from_file(str(glade_file), ("shortcuts-gaphor",))

        shortcuts = builder.get_object("shortcuts-gaphor")
        shortcuts.set_modal(True)
        shortcuts.set_transient_for(self.window)

        shortcuts.show_all()
        return shortcuts
