# vim:sw=4:et

"""A GUI for the checkmodel plugin.
"""

import sys
import gobject
import gtk
import gaphor
from gaphor.ui.abstractwindow import AbstractWindow
from gaphor.plugin import resource
import checkmodel

PYELEMENT_COLUMN = 0
ELEMENT_COLUMN = 1
REASON_COLUMN = 2

class CheckModelWindow(AbstractWindow):

    menu = ('_File', ('FileClose',))

    def __init__(self):
        AbstractWindow.__init__(self)
        # Override the report method
        checkmodel.report = self.on_report

    def construct(self):
        model = gtk.ListStore(gobject.TYPE_PYOBJECT,
                              gobject.TYPE_STRING,
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
        column = gtk.TreeViewColumn("Element", cell, text=ELEMENT_COLUMN)
        treeview.append_column(column)

        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Reason", cell, text=REASON_COLUMN)
        treeview.append_column(column)
        treeview.show()

        self._construct_window(name='checkmodel',
                               title='Check Model',
                               size=(400, 400),
                               contents=scrolled_window)
        self.model = model
        self.treeview = treeview

    def run(self):
        # TODO: Let this run in a Thread(?)
        checkmodel.check_attributes()
        checkmodel.check_associations()

    def on_report(self, element, message):
        log.info('%s: %s' % (type(element).__name__, message))
        model = self.model
        iter = model.append()
        model.set_value(iter, PYELEMENT_COLUMN, element)
        model.set_value(iter, ELEMENT_COLUMN, type(element).__name__)
        model.set_value(iter, REASON_COLUMN, message)
        main = gobject.main_context_default()
        main.iteration(False)

    def on_row_activated(self, treeview, row, column):
        iter = self.model.get_iter(row)
        element = self.model.get_value(iter, PYELEMENT_COLUMN)
        print 'Looking for element', element
        if element.presentation:
            main_window = resource('MainWindow')
            presentation = element.presentation[0]
            diagram = presentation.canvas.diagram
            diagram_tab = main_window.show_diagram(diagram)
            view = diagram_tab.get_view()
            view_item = view.find_view_item(presentation)
            diagram_tab.get_view().focus(view_item)

