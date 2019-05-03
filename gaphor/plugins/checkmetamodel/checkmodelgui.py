"""
A GUI for the checkmodel plugin.
"""

import logging

import gi

from gi.repository import GObject
from gi.repository import Gtk
from zope.interface import implementer

from gaphor.core import inject, action, build_action_group
from gaphor.ui.diagrampage import DiagramPage
from gaphor.abc import ActionProvider
from gaphor.interfaces import IService
from gaphor.plugins.checkmetamodel import checkmodel

PYELEMENT_COLUMN = 0
ELEMENT_COLUMN = 1
REASON_COLUMN = 2

log = logging.getLogger(__name__)


@implementer(IService)
class CheckModelWindow(ActionProvider):

    element_factory = inject("element_factory")
    main_window = inject("main_window")

    menu_xml = """
      <ui>
        <menubar action="mainwindow">
          <menu action="tools">
            <menuitem action="tools-open-check-model" />
          </menu>
        </menubar>
      </ui>"""

    def __init__(self):
        # Override the report method
        checkmodel.report = self.on_report
        self.action_group = build_action_group(self)

    def init(self, app):
        pass

    def shutdown(self):
        pass

    @action(name="tools-open-check-model", label="Check UML model")
    def open(self):
        self.construct()
        self.run()

    def construct(self):
        model = Gtk.ListStore(
            GObject.TYPE_PYOBJECT, GObject.TYPE_STRING, GObject.TYPE_STRING
        )

        treeview = Gtk.TreeView(model)
        treeview.connect("row-activated", self.on_row_activated)
        selection = treeview.get_selection()
        selection.set_mode(Gtk.SelectionMode.SINGLE)
        treeview.set_size_request(200, -1)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_shadow_type(Gtk.ShadowType.IN)
        scrolled_window.add(treeview)
        scrolled_window.show()

        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Element", cell, text=ELEMENT_COLUMN)
        treeview.append_column(column)

        cell = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("Reason", cell, text=REASON_COLUMN)
        treeview.append_column(column)
        treeview.show()

        # self._construct_window(name='checkmodel',
        #                       title='Check Model',
        #                       size=(400, 400),
        #                       contents=scrolled_window)
        self.model = model
        self.treeview = treeview

        self.window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        self.window.connect("destroy", self.on_destroy)
        self.window.set_title("Gaphor - Check Model")
        self.window.add(scrolled_window)
        self.window.set_size_request(400, 400)
        self.window.show()

    def run(self):
        # TODO: Let this run in a Thread(?)
        checkmodel.check_classes(self.element_factory)
        checkmodel.check_attributes(self.element_factory)
        checkmodel.check_associations(self.element_factory)

    def on_report(self, element, message):
        log.info("%s: %s" % (type(element).__name__, message))
        model = self.model
        iter = model.append()
        model.set_value(iter, PYELEMENT_COLUMN, element)
        model.set_value(iter, ELEMENT_COLUMN, type(element).__name__)
        model.set_value(iter, REASON_COLUMN, message)
        main = GObject.main_context_default()
        main.iteration(False)

    def on_row_activated(self, treeview, row, column):
        iter = self.model.get_iter(row)
        element = self.model.get_value(iter, PYELEMENT_COLUMN)
        if element.presentation:
            presentation = element.presentation[0]
            try:
                diagram = presentation.canvas.diagram
            except AttributeError:
                presentation = element.namespace.presentation[0]
                diagram = presentation.canvas.diagram
            diagram_page = DiagramPage(diagram)
            diagram_page.view.focused_item = presentation

    def on_destroy(self, window):
        self.window = None
        self.treeview = None


# vim:sw=4:et
