#!/usr/bin/env python

import logging
import os

from gi.repository import Gtk
from zope.interface import implementer

from gaphor.action import action, build_action_group
from gaphor.core import inject
from gaphor.misc import get_config_dir
from gaphor.interfaces import IActionProvider
from gaphor.misc.console import GTKInterpreterConsole
from gaphor.ui.interfaces import IUIComponent

log = logging.getLogger(__name__)


@implementer(IUIComponent, IActionProvider)
class ConsoleWindow(object):

    component_registry = inject("component_registry")
    main_window = inject("main_window")

    menu_xml = """
        <ui>
          <menubar name="mainwindow">
            <menu action="tools">
              <menuitem action="ConsoleWindow:open" />
            </menu>
          </menubar>
        </ui>
        """

    title = "Gaphor Console"
    size = (400, 400)
    placement = "floating"

    def __init__(self):
        self.action_group = build_action_group(self)
        self.window = None

    def load_console_py(self, console):
        """Load default script for console. Saves some repetitive typing."""

        console_py = os.path.join(get_config_dir(), "console.py")
        try:
            with open(console_py) as f:
                for line in f:
                    console.push(line)
        except IOError:
            log.info("No initiation script %s" % console_py)

    @action(name="ConsoleWindow:open", label="_Console")
    def open_console(self):
        if not self.window:
            self.open()
        else:
            self.window.set_property("has-focus", True)

    def open(self):
        console = self.construct()
        self.load_console_py(console)

    @action(name="ConsoleWindow:close", stock_id="gtk-close", accel="<Primary><Shift>w")
    def close(self, widget=None):
        self.window.destroy()
        self.window = None

    def construct(self):
        window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        window.set_transient_for(self.main_window.window)
        window.set_title(self.title)

        console = GTKInterpreterConsole(
            locals={"service": self.component_registry.get_service}
        )
        console.show()
        window.add(console)
        window.show()

        self.window = window

        window.connect("destroy", self.close)

        return console


# vim:sw=4:et:ai
