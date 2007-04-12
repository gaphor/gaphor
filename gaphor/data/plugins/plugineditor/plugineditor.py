# vim:sw=4:et

"""A GUI for the Plugin Editor.
"""

import sys
import gobject
import pango
import gtk
from zope import component
import gaphor
from gaphor.interfaces import IService
from gaphor.ui.abstractwindow import AbstractWindow
from gaphor.plugin import resource

PLUGIN_COLUMN = 0
NAME_COLUMN = 1
STATUS_COLUMN = 2

class PluginEditorWindow(AbstractWindow):

    menu = ('_File', ('FileClose',))

    def __init__(self):
        AbstractWindow.__init__(self)

    def construct(self):
        model = gtk.ListStore(gobject.TYPE_PYOBJECT,
                              gobject.TYPE_STRING,
                              gobject.TYPE_STRING)

        vbox = gtk.VBox()

        treeview = gtk.TreeView(model)
        treeview.connect('row-activated', self.on_row_activated)
        selection = treeview.get_selection()
        selection.set_mode('single')
        treeview.set_size_request(200, -1)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.set_shadow_type(gtk.SHADOW_IN)
        scrolled_window.add(treeview)
        vbox.pack_start(scrolled_window, expand=True)
        scrolled_window.show()

        #cell = gtk.CellRendererText()
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name", cell, text=NAME_COLUMN)
        treeview.append_column(column)

        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Status", cell, text=STATUS_COLUMN)
        treeview.append_column(column)
        treeview.show()


        detail = gtk.TextView()
        detail.set_wrap_mode(gtk.WRAP_WORD)
        detail.show()

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.set_shadow_type(gtk.SHADOW_IN)
        scrolled_window.add(detail)
        vbox.pack_start(scrolled_window, expand=True)
        scrolled_window.show()
        vbox.show()

        self._construct_window(name='plugineditor',
                               title='Plugin editor',
                               size=(400, 400),
                               contents=vbox)
        self.model = model
        self.treeview = treeview
        self.detail = detail
        
        # Create some nice tags for the text buffer:
        buffer = detail.get_buffer()
        tag = buffer.create_tag('bold')
        tag.set_property('weight', pango.WEIGHT_BOLD)
        tag = buffer.create_tag('indent')
        tag.set_property('font', 'Sans 18')

        treeview.connect_after('cursor_changed', self.on_view_cursor_changed)
        self.update()

    def update(self):
        manager = component.getUtility(IService, 'plugin_manager')
        model = self.model

        for plugin in manager.get_plugins():
            iter = model.append()
            model.set_value(iter, PLUGIN_COLUMN, plugin)
            model.set_value(iter, NAME_COLUMN, plugin.name)
            model.set_value(iter, STATUS_COLUMN, plugin.status)

    def update_detail(self, plugin):
        """Update the detail section with the plugin data
        """
        buffer = self.detail.get_buffer()
        start, end = buffer.get_bounds()
        buffer.delete(start, end)
        
        iter = buffer.get_iter_at_offset(0)

        buffer.insert(iter, 'Name: ')

        mark = buffer.create_mark('insert_mark', iter)
        #start = buffer.get_iter_at_offset(0)
        #buffer.apply_tag_by_name('bold', start, iter)

        buffer.insert(iter, plugin.name)

        start = buffer.get_iter_at_mark(mark)
        buffer.apply_tag_by_name('bold', start, iter)
        mark = buffer.create_mark('insert_mark', iter)

        buffer.insert(iter, '\nVersion: ')
        start = buffer.get_iter_at_mark(mark)
        buffer.apply_tag_by_name('bold', start, iter)
        buffer.insert(iter, plugin.version)

        buffer.insert(iter, '\nAuthor: ')
        buffer.insert(iter, plugin.author)

        buffer.insert(iter, '\nDescription: ')

        start = buffer.get_iter_at_mark(mark)
        buffer.apply_tag_by_name('bold', start, iter)

        buffer.move_mark(mark, iter)

        for line in plugin.description.split('\n'):
            buffer.insert(iter, line.strip())
        start = buffer.get_iter_at_mark(mark)
        iter = buffer.get_end_iter()
        buffer.apply_tag_by_name('indent', start, iter)

        buffer.move_mark(mark, iter)
        buffer.insert(iter, '\nPath: ')
        buffer.insert(iter, plugin.path)
        
        buffer.insert(iter, '\nProvided actions: ')
        buffer.insert(iter, ', '.join(map(getattr, plugin.provided_actions, ['label'] * len(plugin.provided_actions))))


    def on_row_activated(self, treeview, row, column):
        iter = self.model.get_iter(row)
        name = self.model.get_value(iter, NAME_COLUMN)

    def on_view_cursor_changed(self, view):
        selection = view.get_selection()
        model, iter = selection.get_selected()
        if not iter:
            return
        element = model.get_value(iter, PLUGIN_COLUMN)
        self.update_detail(element)

