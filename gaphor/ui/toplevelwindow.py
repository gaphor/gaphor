"""
Basic stuff for toplevel windows.
"""

from builtins import object
import os.path

import gtk
import pkg_resources
from zope import interface

from gaphor.ui.interfaces import IUIComponent

ICONS = (
    'gaphor-24x24.png',
    'gaphor-48x48.png',
    'gaphor-96x96.png',
    'gaphor-256x256.png',
)

class ToplevelWindow(object):

    interface.implements(IUIComponent)

    menubar_path = ''
    toolbar_path = ''
    resizable = True

    def __init__(self):
        self.window = None

    def ui_component(self):
        raise NotImplementedError

    def construct(self):

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_title(self.title)
        self.window.set_size_request(*self.size)
        self.window.set_resizable(self.resizable)

        # set default icons of gaphor windows
        icon_dir = os.path.abspath(pkg_resources.resource_filename('gaphor.ui', 'pixmaps'))
        icons = (gtk.gdk.pixbuf_new_from_file(os.path.join(icon_dir, f)) for f in ICONS)
        self.window.set_icon_list(*icons)

        self.window.add_accel_group(self.ui_manager.get_accel_group())

        
        if self.menubar_path or self.toolbar_path:
            # Create a full featured window.
            vbox = gtk.VBox()
            self.window.add(vbox)
            vbox.show()

            menubar = self.ui_manager.get_widget(self.menubar_path)
            if menubar:
                vbox.pack_start(menubar, expand=False)
            
            toolbar = self.ui_manager.get_widget(self.toolbar_path)
            if toolbar:
                vbox.pack_start(toolbar, expand=False)

            vbox.pack_end(self.ui_component(), expand=self.resizable)
            vbox.show()
            # TODO: add statusbar
        else:
            # Create a simple window.
            self.window.add(self.ui_component())
        self.window.show()


# vim:sw=4:et:ai
