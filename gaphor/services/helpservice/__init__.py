"""About and help services.

(help browser anyone?)
"""

import importlib

import importlib_metadata
from gi.repository import Gtk

from gaphor.abc import ActionProvider, Service
from gaphor.core import action
from gaphor.diagram.uibuilder import translated_ui_string


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
        builder.add_objects_from_string(
            translated_ui_string("gaphor.services.helpservice", "about.ui"), ("about",)
        )

        about = builder.get_object("about")

        about.set_version(importlib_metadata.version("gaphor"))
        about.set_modal(True)
        about.set_transient_for(self.window)

        about.run()
        about.destroy()

    @action(name="app.shortcuts")
    def shortcuts(self):
        builder = Gtk.Builder()
        builder.add_objects_from_string(
            translated_ui_string("gaphor.services.helpservice", "shortcuts.ui"),
            ("shortcuts-gaphor",),
        )

        shortcuts = builder.get_object("shortcuts-gaphor")
        shortcuts.set_modal(True)
        shortcuts.set_transient_for(self.window)

        shortcuts.show()
        return shortcuts
