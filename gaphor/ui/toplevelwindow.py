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

        self.window.add_accel_group(self.ui_manager.get_accel_group())

        vbox = gtk.VBox()
        self.window.add(vbox)
        vbox.show()

        #self.ui_manager.insert_action_group(self.action_group, 0)
        #self.ui_manager.add_ui_from_string(self.menu_xml)

        menubar = self.ui_manager.get_widget(self.menubar_path)
        if menubar:
            vbox.pack_start(menubar, expand=False)
            #menubar.show()
        
        if self.toolbar_path:
            toolbar = self.ui_manager.get_widget(self.toolbar_path)
            if toolbar:
                vbox.pack_start(toolbar, expand=False)
                #toolbar.show()

        vbox.pack_end(self.ui_component(), expand=True)
        vbox.show()
        # TODO: add statusbar
        self.window.show()


# vim:sw=4:et:ai
