"""Service dedicated to exporting diagrams to a variety of file formats."""

import os
import logging

import cairo
from gaphas.freehand import FreeHandPainter
from gaphas.painter import ItemPainter, BoundingBoxPainter
from gaphas.view import View
from zope.interface import implementer

from gaphor.core import _, inject, action, build_action_group
from gaphor.abc import Service, ActionProvider
from gaphor.ui.abc import UIComponent
from gaphor.ui.filedialog import FileDialog
from gaphor.ui.questiondialog import QuestionDialog

logger = logging.getLogger(__name__)


class DiagramExportManager(Service, ActionProvider):
    """
    Service for exporting diagrams as images (SVG, PNG, PDF).
    """

    component_registry = inject("component_registry")
    main_window = inject("main_window")
    properties = inject("properties")

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
        pass

    def get_current_diagram(self):
        return self.component_registry.get(
            UIComponent, "diagrams"
        ).get_current_diagram()

    def save_dialog(self, diagram, title, ext):

        filename = (diagram.name or "export") + ext
        file_dialog = FileDialog(title, action="save", filename=filename)

        save = False
        while True:
            filename = file_dialog.selection
            if os.path.exists(filename):
                question = (
                    _(
                        "The file %s already exists. Do you want to "
                        "replace it with the file you are exporting "
                        "to?"
                    )
                    % filename
                )
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

        logger.info("Updating painters")
        logger.debug("View is %s" % view)

        sloppiness = self.properties("diagram.sloppiness", 0)

        logger.debug("Sloppiness is %s" % sloppiness)

        if sloppiness:
            view.painter = FreeHandPainter(ItemPainter(), sloppiness)
            view.bounding_box_painter = FreeHandPainter(
                BoundingBoxPainter(), sloppiness
            )
        else:
            view.painter = ItemPainter()

    def save_svg(self, filename, canvas):

        logger.info("Exporting to SVG")
        logger.debug("SVG path is %s" % filename)

        view = View(canvas)

        self.update_painters(view)

        # Update bounding boxes with a temporary CairoContext
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

        logger.info("Exporting to PNG")
        logger.debug("PNG path is %s" % filename)

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
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w + 1), int(h + 1))
        cr = cairo.Context(surface)
        view.matrix.translate(-view.bounding_box.x, -view.bounding_box.y)
        view.paint(cr)
        cr.show_page()
        surface.write_to_png(filename)

    def save_pdf(self, filename, canvas):

        logger.info("Exporting to PDF")
        logger.debug("PDF path is %s" % filename)

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

    @action(
        name="file-export-svg",
        label="Export to SVG",
        tooltip="Export the diagram to SVG",
    )
    def save_svg_action(self):
        title = "Export diagram to SVG"
        ext = ".svg"
        diagram = self.get_current_diagram()
        filename = self.save_dialog(diagram, title, ext)
        if filename:
            self.save_svg(filename, diagram.canvas)

    @action(
        name="file-export-png",
        label="Export to PNG",
        tooltip="Export the diagram to PNG",
    )
    def save_png_action(self):
        title = "Export diagram to PNG"
        ext = ".png"
        diagram = self.get_current_diagram()
        filename = self.save_dialog(diagram, title, ext)
        if filename:
            self.save_png(filename, diagram.canvas)

    @action(
        name="file-export-pdf",
        label="Export to PDF",
        tooltip="Export the diagram to PDF",
    )
    def save_pdf_action(self):
        title = "Export diagram to PDF"
        ext = ".pdf"
        diagram = self.get_current_diagram()
        filename = self.save_dialog(diagram, title, ext)
        if filename:
            self.save_pdf(filename, diagram.canvas)


# vim:sw=4:et:
