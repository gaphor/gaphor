#!/usr/bin/env python
# vim: sw=4:et

import sys
import gtk
import gaphor
from gaphor.interfaces import IActionProvider
from gaphor.ui.interfaces import IUIComponent
from gaphor.action import action, build_action_group
from gaphor.misc.console import GTKInterpreterConsole
from zope import interface

class ConsoleWindow(object):
    
    interface.implements(IActionProvider, IUIComponent)

    menu_xml = """
        <ui>
          <menubar action="mainwindow">
            <menu name="_Window" action="Menu">
              <menuitem name='_Console' action="ConsoleWindow:open" />
            </menu>
          </menubar>
          <menubar action="consolewindow">
            <menu name="_File" action="Menu">
              <menuitem name='_Close' action="ConsoleWindow:close" />
            </menu>
          </menubar>
        </ui>
        """

    title = 'Gaphor Console'
    size = (400, 400)
    menubar_path = '/consolewindow'
    toolbar_path = ''

    def __init__(self):
        self.action_group = build_action_group(self)
        self.window = None
        self.ui_manager = None # injected

    def ui_component(self):
        console = GTKInterpreterConsole()
        console.show()
        return console

    def construct(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(self.title)
        self.window.set_size_request(*self.size)
        self.window.set_resizable(True)

        vbox = gtk.VBox()
        self.window.add(vbox)
        vbox.show()

        self.ui_manager.insert_action_group(self.action_group, 0)
        self.ui_manager.add_ui_from_string(self.menu_xml)

        self.window.add_accel_group(self.ui_manager.get_accel_group())

        menubar = self.ui_manager.get_widget(self.menubar_path)
        vbox.pack_start(menubar, expand=False)
        
        if self.toolbar_path:
            toolbar = self.ui_manager.get_widget(self.toolbar_path)
            vbox.pack_start(toolbar, expand=False)

        vbox.pack_end(self.ui_component(), expand=True)

        # TODO: add statusbar
        self.window.show_all()

    @action(name='Menu', label='_File')
    def dummy(self): pass

    @action(name='ConsoleWindow:open', label='Console')
    def open(self):
        if not self.window:
            self.construct()
        else:
            self.window.show_all()

    @action(name='ConsoleWindow:close', stock_id='gtk-close')
    def close(self):
        self.window.destroy()
        self.window = None

