#!/usr/bin/env python

import logging
import os

from zope.interface import implementer

from gaphor.action import action, open_action, build_action_group
from gaphor.core import inject
from gaphor.misc import get_config_dir
from gaphor.interfaces import IActionProvider
from gaphor.misc.console import GTKInterpreterConsole
from gaphor.ui.interfaces import IUIComponent

log = logging.getLogger(__name__)


@implementer(IUIComponent, IActionProvider)
class ConsoleWindow(object):

    component_registry = inject("component_registry")

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
        self.console = None
        self.ui_manager = None  # injected

    def load_console_py(self):
        """Load default script for console. Saves some repetitive typing."""

        console_py = os.path.join(get_config_dir(), "console.py")
        try:
            with open(console_py) as f:
                for line in f:
                    self.console.push(line)
        except IOError:
            log.info("No initiation script %s" % console_py)

    @open_action(name="ConsoleWindow:open", label="_Console")
    def open_console(self):
        if not self.console:
            return self
        else:
            self.console.set_property("has-focus", True)

    def open(self):
        self.construct()
        self.load_console_py()
        return self.console

    @action(name="ConsoleWindow:close", stock_id="gtk-close", accel="<Primary><Shift>w")
    def close(self, dock_item=None):
        self.console.destroy()
        self.console = None

    def construct(self):
        console = GTKInterpreterConsole(
            locals={"service": self.component_registry.get_service}
        )
        console.show()
        self.console = console
        return console


# vim:sw=4:et:ai
