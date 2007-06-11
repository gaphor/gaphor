"""
Code reverse engineer plugin for Python source code.

This plugin uses PyNSource, written by Andy Bulka
[http://www.atug.com/andypatterns/pynsource.htm].

Depends on the Diagram Layout plugin.
"""

__plugin__ = 'PyNSource'
__version__ = '0.1'
__author__ = 'Arjan Molenaar'

import gobject
import gtk
from zope import interface, component
from gaphor.core import _, inject, action, build_action_group
from gaphor.interfaces import IService, IActionProvider

from engineer import Engineer


NAME_COLUMN = 0


class PyNSource(object):

    interface.implements(IService, IActionProvider)

    gui_manager = inject('gui_manager')

    menu_xml = """
      <ui>
        <menubar action="mainwindow">
          <menu action="file">
            <menu action="file-import">
              <menuitem action="file-import-pynsource" />
            </menu>
          </menu>
        </menubar>
      </ui>"""

    def __init__(self):
        self.win = None
        self.action_group = build_action_group(self)

    def init(self, app):
        pass

    def shutdown(self):
        pass

    @action(name='file-import-pynsource', label='Python source code',
            tooltip='Import Python source code')
    def execute(self):
        dialog = self.create_dialog()
        response = dialog.run()

        if response != gtk.RESPONSE_OK:
            dialog.destroy()
            self.reset()
            return

        files = []
        for row in self.filelist:
            files.append(row[0])

        dialog.destroy()

        self.process(files)
        self.reset()

    def process(self, files):
        """Create a diagram based on a list of files.
        """
        engineer = Engineer()
        engineer.process(files)

        main_window = self.gui_manager.main_window
        # Open and select the new diagram in the main window:
        main_window.select_element(engineer.diagram)
        main_window.show_diagram(engineer.diagram)

    def create_dialog(self):
        dialog = gtk.Dialog("Import Python files",
                            self.gui_manager.main_window.window,
                            gtk.DIALOG_MODAL,
                            (gtk.STOCK_OK, gtk.RESPONSE_OK,
                             gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        dialog.set_default_response(gtk.RESPONSE_OK)

        filelist = gtk.ListStore(gobject.TYPE_STRING)
        filelist.connect('row-inserted', self.on_view_rows_changed)
        filelist.connect('row-deleted', self.on_view_rows_changed)

        hbox = gtk.HBox()

        frame = gtk.Frame('Files to reverse-engineer')
        frame.set_border_width(8)
        frame.set_size_request(300, 200)
        frame.show()
        hbox.pack_start(frame, expand=True)

        treeview = gtk.TreeView(filelist)
        treeview.set_property('headers-visible', False)
        selection = treeview.get_selection()
        selection.set_mode('single')
        treeview.set_size_request(200, -1)
        treeview.connect_after('cursor_changed', self.on_view_cursor_changed)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.set_shadow_type(gtk.SHADOW_IN)
        scrolled_window.set_border_width(4)
        scrolled_window.add(treeview)
        frame.add(scrolled_window)
        scrolled_window.show()

        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Filename", cell, text=NAME_COLUMN)
        treeview.append_column(column)

        bbox = gtk.VButtonBox()
        bbox.set_layout(gtk.BUTTONBOX_SPREAD)
        bbox.set_border_width(10)
        button = gtk.Button(stock='gtk-add')
        button.connect('clicked', self.on_add_clicked)
        bbox.add(button)
        self.add_button = button

        button = gtk.Button('Add dir...')
        button.connect('clicked', self.on_add_dir_clicked)
        bbox.add(button)
        self.add_dir_button = button

        button = gtk.Button(stock='gtk-remove')
        button.connect('clicked', self.on_remove_clicked)
        button.set_property('sensitive', False)
        bbox.add(button)
        self.remove_button = button

        #button = gtk.Button(stock='gtk-execute')
        #button.connect('clicked', self.on_execute_clicked)
        #button.set_property('sensitive', False)
        #bbox.add(button)
        #self.execute_button = button

        hbox.pack_start(bbox, expand=False)
        hbox.show_all()

        dialog.vbox.pack_start(hbox, True, True, 0)

        self.filelist = filelist
        self.treeview = treeview
        
        return dialog

    def reset(self):
        self.add_button = None
        self.add_dir_button = None
        self.remove_button = None
        self.treeview = None
        self.filelist = None

    def on_view_cursor_changed(self, view):
        selection = view.get_selection()
        filelist, iter = selection.get_selected()
        if not iter:
            self.remove_button.set_property('sensitive', False)
            return
        #element = filelist.get_value(iter, NAME_COLUMN)
        self.remove_button.set_property('sensitive', True)
        #self.update_detail(element)

    def on_view_rows_changed(self, view, *args):
        iter = None
        try:
            iter = view.get_iter('0')
        except ValueError:
            pass
        self.execute_button.set_property('sensitive', bool(iter))

    def on_add_clicked(self, button):
        filesel = gtk.FileSelection('Open Python file')
        filesel.hide_fileop_buttons()
        response = filesel.run()
        filename = filesel.get_filename()
        filesel.destroy()
        if filename and response == gtk.RESPONSE_OK:
            iter = self.filelist.append()
            self.filelist.set_value(iter, NAME_COLUMN, filename)
            #self.execute_button.set_property('

    def on_add_dir_clicked(self, button):
        pass

    def on_remove_clicked(self, button):
        selection = self.treeview.get_selection()
        filelist, iter = selection.get_selected()
        if not iter:
            return
        element = filelist.remove(iter)
        
        self.remove_button.set_property('sensitive', False)


# vim:sw=4:et:ai
