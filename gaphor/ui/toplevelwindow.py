"""
Basic stuff for toplevel windows.
"""

import gtk

from zope import interface
from interfaces import IUIComponent


class ToplevelWindow(object):

    interface.implements(IUIComponent)

    menubar_path = ''
    toolbar_path = ''

    def __init__(self):
        self.window = None

    def construct(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(self.title)
        self.window.set_size_request(*self.size)
        self.window.set_resizable(True)

        vbox = gtk.VBox()
        self.window.add(vbox)
        vbox.show()

        #self.ui_manager.insert_action_group(self.action_group, 0)
        #self.ui_manager.add_ui_from_string(self.menu_xml)

        self.window.add_accel_group(self.ui_manager.get_accel_group())

        menubar = self.ui_manager.get_widget(self.menubar_path)
        vbox.pack_start(menubar, expand=False)
        
        if self.toolbar_path:
            toolbar = self.ui_manager.get_widget(self.toolbar_path)
            vbox.pack_start(toolbar, expand=False)

        vbox.pack_end(self.ui_component(), expand=True)

        # TODO: add statusbar
        self.window.show_all()


# vim:sw=4:et:ai
