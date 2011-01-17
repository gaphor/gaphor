"""
Basic stuff for toplevel windows.
"""

import os.path
import pkg_resources

import gtk
from etk.docking import DockGroup, DockItem
from etk.docking.docklayout import add_new_group_floating
from zope import interface
from interfaces import IUIComponent
from gaphor.core import inject


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


class UtilityWindow(object):

    interface.implements(IUIComponent)

    gui_manager = inject('gui_manager')

    title = '<<Gaphor>>'
    resizable = False

    def construct(self):
        layout = self.gui_manager.main_window.layout
        new_group = DockGroup()
        new_item = DockItem(self.title)
        new_group.insert_item(new_item)
        self.dock_item = new_item
        ui_component = self.ui_component()
        if ui_component:
            new_item.add(ui_component)
        add_new_group_floating(new_group, layout, self.size)
        return new_item


# vim:sw=4:et:ai
