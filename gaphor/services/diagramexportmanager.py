#!/usr/bin/env python

# Copyright (C) 2007-2017 Adam Boduch <adam.boduch@gmail.com>
#                         Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
Service dedicated to exporting diagrams to a varyity of file formats.
"""

from __future__ import absolute_import
import os
import cairo

from zope import interface, component

from logging import getLogger
from gaphor.core import _, inject, action, build_action_group
from gaphor.interfaces import IService, IActionProvider
from gaphor.ui.filedialog import FileDialog
from gaphor.ui.questiondialog import QuestionDialog

from gaphas.view import View
from gaphas.painter import ItemPainter, BoundingBoxPainter
from gaphas.freehand import FreeHandPainter

class DiagramExportManager(object):
    """
    Service for exporting diagrams as images (SVG, PNG, PDF).
    """

    interface.implements(IService, IActionProvider)

    main_window = inject('main_window')
    properties = inject('properties')
    logger = getLogger('ExportManager')

    menu_xml = """
      <ui>
        <menubar action="mainwindow">
          <menu action="file">
            <menu action="file-export">
              <menuitem action="file-export-svg" />
              <menuitem action="file-export-png" />
              <menuitem action="file-export-pdf" />
              <separator />
            </menu>
          </menu>
        </menubar>
      </ui>
    """

    def __init__(self):
        self.action_group = build_action_group(self)

    def init(self, app):
        pass

    def shutdown(self):
        pass

    def update(self):
        
        self.logger.info('Updating')
        
        tab = self.get_window().get_current_diagram_tab()
        self.sensitive = tab and True or False

    def save_dialog(self, diagram, title, ext):
        
        filename = (diagram.name or 'export') + ext
        file_dialog = FileDialog(title, action='save', filename=filename)
        
        save = False
        while True:
            filename = file_dialog.selection
            if os.path.exists(filename):
                question = _("The file %s already exists. Do you want to "\
                             "replace it with the file you are exporting "\
                             "to?") % filename
                question_dialog = QuestionDialog(question)
                answer = question_dialog.answer
                question_dialog.destroy()
                if answer:
                    save = True
                    break
            else:
                save = True
                break
                
        file_dialog.destroy()
        
        if save and filename:
            return filename                
        
    def update_painters(self, view):
        
        self.logger.info('Updating painters')
        self.logger.debug('View is %s' % view)
        
        sloppiness = self.properties('diagram.sloppiness', 0)
        
        self.logger.debug('Sloppiness is %s' % sloppiness)
        
        if sloppiness:
            view.painter = FreeHandPainter(ItemPainter(), sloppiness)
            view.bounding_box_painter = FreeHandPainter(BoundingBoxPainter(), sloppiness)
        else:
            view.painter = ItemPainter()

    def save_svg(self, filename, canvas):
        
        self.logger.info('Exporting to SVG')
        self.logger.debug('SVG path is %s' % filename)
        
        view = View(canvas)

        self.update_painters(view)

        # Update bounding boxes with a temporaly CairoContext
        # (used for stuff like calculating font metrics)
        tmpsurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
        tmpcr = cairo.Context(tmpsurface)
        view.update_bounding_box(tmpcr)
        tmpcr.show_page()
        tmpsurface.flush()

        w, h = view.bounding_box.width, view.bounding_box.height
        surface = cairo.SVGSurface(filename, w, h)
        cr = cairo.Context(surface)
        view.matrix.translate(-view.bounding_box.x, -view.bounding_box.y)
        view.paint(cr)
        cr.show_page()
        surface.flush()
        surface.finish()


    def save_png(self, filename, canvas):
        
        self.logger.info('Exporting to PNG')
        self.logger.debug('PNG path is %s' % filename)
        
        view = View(canvas)

        self.update_painters(view)

        # Update bounding boxes with a temporaly CairoContext
        # (used for stuff like calculating font metrics)
        tmpsurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
        tmpcr = cairo.Context(tmpsurface)
        view.update_bounding_box(tmpcr)
        tmpcr.show_page()
        tmpsurface.flush()

        w, h = view.bounding_box.width, view.bounding_box.height
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w+1), int(h+1))
        cr = cairo.Context(surface)
        view.matrix.translate(-view.bounding_box.x, -view.bounding_box.y)
        view.paint(cr)
        cr.show_page()
        surface.write_to_png(filename)

    def save_pdf(self, filename, canvas):
        
        self.logger.info('Exporting to PDF')
        self.logger.debug('PDF path is %s' % filename)
        
        view = View(canvas)

        self.update_painters(view)

        # Update bounding boxes with a temporaly CairoContext
        # (used for stuff like calculating font metrics)
        tmpsurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
        tmpcr = cairo.Context(tmpsurface)
        view.update_bounding_box(tmpcr)
        tmpcr.show_page()
        tmpsurface.flush()

        w, h = view.bounding_box.width, view.bounding_box.height
        surface = cairo.PDFSurface(filename, w, h)
        cr = cairo.Context(surface)
        view.matrix.translate(-view.bounding_box.x, -view.bounding_box.y)
        view.paint(cr)
        cr.show_page()
        surface.flush()
        surface.finish()

    @action(name='file-export-svg', label='Export to SVG',
            tooltip='Export the diagram to SVG')
    def save_svg_action(self):
        title = 'Export diagram to SVG'
        ext = '.svg'
        diagram = self.main_window.get_current_diagram()
        filename = self.save_dialog(diagram, title, ext)
        if filename:
            self.save_svg(filename, diagram.canvas)


    @action(name='file-export-png', label='Export to PNG',
            tooltip='Export the diagram to PNG')
    def save_png_action(self):
        title = 'Export diagram to PNG'
        ext = '.png'
        diagram = self.main_window.get_current_diagram()
        filename = self.save_dialog(diagram, title, ext)
        if filename:
            self.save_png(filename, diagram.canvas)


    @action(name='file-export-pdf', label='Export to PDF',
            tooltip='Export the diagram to PDF')
    def save_pdf_action(self):
        title = 'Export diagram to PDF'
        ext = '.pdf'
        diagram = self.main_window.get_current_diagram()
        filename = self.save_dialog(diagram, title, ext)
        if filename:
            self.save_pdf(filename, diagram.canvas)


# vim:sw=4:et:

