#!/usr/bin/env python

import logging
import os

from gi.repository import Gdk, Gtk

if Gtk.get_major_version() == 4:
    from gi.repository import Adw

from gaphor.abc import ActionProvider
from gaphor.action import action
from gaphor.i18n import gettext
from gaphor.plugins.console.console import GTKInterpreterConsole
from gaphor.services.properties import get_config_dir
from gaphor.ui.abc import UIComponent

log = logging.getLogger(__name__)


class ConsoleWindow(UIComponent, ActionProvider):

    title = gettext("Gaphor Console")
    size = (400, 400)

    def __init__(self, component_registry, main_window, tools_menu):
        self.component_registry = component_registry
        self.main_window = main_window
        tools_menu.add_actions(self)
        self.window = None

    def load_console_py(self, console):
        """Load default script for console.

        Saves some repetitive typing.
        """

        console_py = os.path.join(get_config_dir(), "console.py")
        try:
            with open(console_py) as f:
                for line in f:
                    console.push(line)
        except OSError:
            log.info(f"No initiation script {console_py}")

    @action(name="console-window-open", label=gettext("Console"))
    def open_console(self):
        if not self.window:
            self.open()
        else:
            self.window.present()

    def open(self):
        console = self.construct()
        self.load_console_py(console)

    def close(self, widget=None):
        if self.window:
            self.window.destroy()
            self.window = None

    def construct(self):
        window = (
            Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
            if Gtk.get_major_version() == 3
            else Adw.Window.new()
        )
        window.set_transient_for(self.main_window.window)
        window.set_title(self.title)
        window.set_default_size(700, 480)

        element_factory = self.component_registry.get_service("element_factory")
        console = GTKInterpreterConsole(
            locals={
                "service": self.component_registry.get_service,
                "select": element_factory.lselect,
            }
        )
        if Gtk.get_major_version() == 3:
            console.show()
            window.add(console)
            window.connect("destroy", self.close)
        else:
            box = Gtk.Box(orientation="vertical")
            header_bar = Gtk.HeaderBar()
            box.append(header_bar)
            box.append(console)
            window.set_content(box)
            window.connect("close-request", self.close)
        window.show()
        self.window = window

        def key_event(widget, keyval, keycode, state):
            if keyval == Gdk.KEY_d and state & Gdk.ModifierType.CONTROL_MASK:
                self.close()
            return False

        console.text_controller.connect("key-pressed", key_event)

        return console
