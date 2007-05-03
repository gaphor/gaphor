#!/usr/bin/env python
# vim: sw=4:et

import sys
import gtk
import gaphor
from gaphor.interfaces import IActionProvider
from gaphor.action import action, build_action_group
from gaphor.misc.console import GTKInterpreterConsole
from zope import interface

class ConsoleWindow(object):
    
    interface.implements(IActionProvider)

    menu_xml = """
        <ui>
          <menubar action="consolewindow">
            <menu name="_File" action="FileMenu">
              <menuitem name='_Close' action="ConsoleWindow_close" />
            </menu>
          </menubar>
        </ui>
        """

    #action_group = property(lambda s: s._action_group)

    def __init__(self):
        self.action_group = build_action_group(self)

    def construct(self):
        console = GTKInterpreterConsole()
        console.show()

        #self._construct_window(name='console',
        #                       title='Gaphor Console',
        #                       size=(400, 400),
        #                       contents=console)
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title('Gaphor Console')
        self.window.set_size_request(400, 400)
        self.window.set_resizable(True)

        self.ui_manager = gtk.UIManager()
        self.ui_manager.insert_action_group(self.action_group, 0)
        self.ui_manager.add_ui_from_string(self.menu_xml)

        menubar = self.ui_manager.get_widget('/consolewindow')

        vbox = gtk.VBox()
        self.window.add(vbox)
        vbox.show()

        vbox.pack_start(menubar, expand=False)
        vbox.pack_end(console, expand=True)

        # TODO: add statusbar
        self.window.show_all()

    @action(name='FileMenu', label='_File')
    def dummy(self): pass

    @action(name='ConsoleWindow_close', label='_Close', stock_id='gtk-close')
    def close(self):
        self.window.destroy()
        
    def _on_window_destroy():
        pass

