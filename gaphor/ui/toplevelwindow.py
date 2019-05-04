"""
Basic stuff for toplevel windows.
"""

import os.path

from gi.repository import GdkPixbuf
from gi.repository import Gtk
import pkg_resources
from zope.interface import implementer

from gaphor.core import inject
from gaphor.ui.abc import UIComponent

ICONS = (
    "gaphor-24x24.png",
    "gaphor-48x48.png",
    "gaphor-96x96.png",
    "gaphor-256x256.png",
)


class ToplevelWindow(UIComponent):

    menubar_path = ""
    toolbar_path = ""
    resizable = True

    action_manager = inject("action_manager")

    def __init__(self):
        self.window = None

    def ui_component(self):
        raise NotImplementedError

    def construct(self):

        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.set_title(self.title)
        self.window.set_size_request(*self.size)
        self.window.set_resizable(self.resizable)

        # set default icons of gaphor windows
        icon_dir = os.path.abspath(
            pkg_resources.resource_filename("gaphor.ui", "pixmaps")
        )
        icons = (
            GdkPixbuf.Pixbuf.new_from_file(os.path.join(icon_dir, f)) for f in ICONS
        )
        self.window.set_icon_list(*icons)

        self.window.add_accel_group(self.action_manager.get_accel_group())

        if self.menubar_path or self.toolbar_path:
            # Create a full featured window.
            vbox = Gtk.VBox()
            self.window.add(vbox)
            vbox.show()

            menubar = self.action_manager.get_widget(self.menubar_path)
            if menubar:
                vbox.pack_start(child=menubar, expand=False, fill=True, padding=0)

            toolbar = self.action_manager.get_widget(self.toolbar_path)
            if toolbar:
                vbox.pack_start(child=toolbar, expand=False, fill=True, padding=0)

            vbox.pack_end(
                child=self.ui_component, expand=self.resizable, fill=True, padding=0
            )
            vbox.show()
            # TODO: add statusbar
        else:
            # Create a simple window.
            self.window.add(self.ui_component())
        self.window.show()
