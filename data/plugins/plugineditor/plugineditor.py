# vim:sw=4:et

"""A GUI for the Plugin Editor.
"""

import sys
import gobject
import gtk
import gaphor
from gaphor.ui.abstractwindow import AbstractWindow
from gaphor.plugin import resource

NAME_COLUMN = 0
STATUS_COLUMN = 1

class PluginEditorWindow(AbstractWindow):

    menu = ('_File', ('FileClose',))

    def __init__(self):
        AbstractWindow.__init__(self)

    def construct(self):
        model = gtk.ListStore(gobject.TYPE_STRING,
                              gobject.TYPE_STRING)

        treeview = gtk.TreeView(model)
        treeview.connect('row-activated', self.on_row_activated)
        selection = treeview.get_selection()
        selection.set_mode('single')
        treeview.set_size_request(200, -1)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.set_shadow_type(gtk.SHADOW_IN)
        scrolled_window.add(treeview)
        scrolled_window.show()

        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name", cell, text=NAME_COLUMN)
        treeview.append_column(column)

        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Status", cell, text=STATUS_COLUMN)
        treeview.append_column(column)
        treeview.show()

        self._construct_window(name='plugineditor',
                               title='Plugin editor',
                               size=(400, 400),
                               contents=scrolled_window)
        self.model = model
        self.treeview = treeview

        self.update()

    def update(self):
        manager = resource('PluginManager')
        model = self.model

        for plugin in manager.get_plugins():
            iter = model.append()
            model.set_value(iter, NAME_COLUMN, plugin.name)
            model.set_value(iter, STATUS_COLUMN, plugin.status)

    def on_row_activated(self, treeview, row, column):
        iter = self.model.get_iter(row)
        name = self.model.get_value(iter, NAME_COLUMN)

