#!/usr/bin/env python

# Copyright (C) 2004-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License 
# more details.
#
# You should have received a copy of the GNU Library General Public 
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
A GUI for the checkmodel plugin.
"""

from __future__ import absolute_import
from __future__ import print_function

import gobject
import gtk
from zope import interface

from . import checkmodel

from gaphor.core import inject, action, build_action_group
from gaphor.interfaces import IService, IActionProvider

PYELEMENT_COLUMN = 0
ELEMENT_COLUMN = 1
REASON_COLUMN = 2

class CheckModelWindow(object):

    interface.implements(IService, IActionProvider)

    element_factory = inject('element_factory')
    main_window = inject('main_window')

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

    @action(name='tools-open-check-model', label='Check UML model')
    def open(self):
        self.construct()
        self.run()

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

        #self._construct_window(name='checkmodel',
        #                       title='Check Model',
        #                       size=(400, 400),
        #                       contents=scrolled_window)
        self.model = model
        self.treeview = treeview

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect('destroy', self.on_destroy)
        self.window.set_title('Gaphor - Check Model')
        self.window.add(scrolled_window)
        self.window.set_size_request(400, 400)
        self.window.show()
        
        
    def run(self):
        # TODO: Let this run in a Thread(?)
        checkmodel.check_classes(self.element_factory)
        checkmodel.check_attributes(self.element_factory)
        checkmodel.check_associations(self.element_factory)

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
        print('Looking for element', element)
        if element.presentation:
            main_window = self.main_window
            presentation = element.presentation[0]
            try:
                diagram = presentation.canvas.diagram
            except AttributeError:
                presentation = element.namespace.presentation[0]
                diagram = presentation.canvas.diagram
            diagram_tab = main_window.show_diagram(diagram)
            diagram_tab.view.focused_item = presentation

    def on_destroy(self, window):
        self.window = None
        self.treeview = None

# vim:sw=4:et
