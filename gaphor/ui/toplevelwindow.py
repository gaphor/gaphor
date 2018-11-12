"""
Basic stuff for toplevel windows.
"""

import os.path
from builtins import object

from gi.repository import Gtk
import pkg_resources
from zope.interface import implementer

from gaphor.ui.interfaces import IUIComponent

ICONS = (
    'gaphor-24x24.png',
    'gaphor-48x48.png',
    'gaphor-96x96.png',
    'gaphor-256x256.png',
)


@implementer(IUIComponent)
class ToplevelWindow(object):

    menubar_path = ''
    toolbar_path = ''
    resizable = True

    def __init__(self):
        self.window = None

    def construct(self):

        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.set_title(self.title)
        self.window.set_size_request(*self.size)
        self.window.set_resizable(self.resizable)

        # set default icons of gaphor windows
        icon_dir = os.path.abspath(pkg_resources.resource_filename('gaphor.ui', 'pixmaps'))
        icons = (GdkPixbuf.Pixbuf.new_from_file(os.path.join(icon_dir, f)) for f in ICONS)
        self.window.set_icon_list(*icons)

        self.window.add_accel_group(self.ui_manager.get_accel_group())

        
        if self.menubar_path or self.toolbar_path:
            # Create a full featured window.
            vbox = Gtk.VBox()
            self.window.add(vbox)
            vbox.show()

            menubar = self.ui_manager.get_widget(self.menubar_path)
            if menubar:
                vbox.pack_start(menubar, False, True, 0)
            
            toolbar = self.ui_manager.get_widget(self.toolbar_path)
            if toolbar:
                vbox.pack_start(toolbar, False, True, 0)

            vbox.pack_end(self.ui_component(, True, True, 0), expand=self.resizable)
            vbox.show()
            # TODO: add statusbar
        else:
            # Create a simple window.
            self.window.add(self.ui_component())
        self.window.show()


class UtilityWindow(ToplevelWindow):

    gui_manager = inject('gui_manager')

    resizable = False

    def construct(self):
        super(UtilityWindow, self).construct()

        main_window = self.gui_manager.main_window.window
        self.set_transient_for(main_window)
        #self.window.set_keep_above(True)
        self.window.set_property('skip-taskbar-hint', True)
        self.window.set_position(Gtk.WindowPosition.MOUSE)
        self.window.show()
       #self.set_type_hint(Gdk.WindowTypeHint.UTILITY)


# vim:sw=4:et:ai
