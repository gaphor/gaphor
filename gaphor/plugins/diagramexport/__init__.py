"""Service dedicated to exporting diagrams to a variety of file formats."""

import logging
import os

import cairo
from gaphas.painter import BoundingBoxPainter, FreeHandPainter
from gaphas.view import GtkView

from gaphor.abc import ActionProvider, Service
from gaphor.core import action, gettext
from gaphor.core.modeling.diagram import StyledDiagram
from gaphor.diagram.painter import ItemPainter
from gaphor.ui.filedialog import save_file_dialog
from gaphor.ui.questiondialog import QuestionDialog

logger = logging.getLogger(__name__)


def new_painter(diagram):
    style = diagram.style(StyledDiagram(diagram))

    sloppiness = style.get("line-style", 0.0)

    if sloppiness:
        return FreeHandPainter(ItemPainter(), sloppiness)
    else:
        return ItemPainter()


class DiagramExport(Service, ActionProvider):
    """Service for exporting diagrams as images (SVG, PNG, PDF)."""

    def __init__(self, diagrams=None, export_menu=None):
        self.diagrams = diagrams
        self.export_menu = export_menu
        if export_menu:
            export_menu.add_actions(self)

    def shutdown(self):
        if self.export_menu:
            self.export_menu.remove_actions(self)

    def save_dialog(self, diagram, title, ext, mime_type):
        dot_ext = f".{ext}"
        filename = (diagram.name or "export") + dot_ext
        return save_file_dialog(
            title,
            filename=filename,
            extension=ext,
            filters=[
                (gettext("All {ext} Files").format(ext=ext.upper()), dot_ext, mime_type)
            ],
        )

    def render(self, diagram, new_surface):
        diagram.update_now(diagram.get_all_items())

        painter = new_painter(diagram)

        # Update bounding boxes with a temporary CairoContext
        # (used for stuff like calculating font metrics)
        tmpsurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
        tmpcr = cairo.Context(tmpsurface)
        bounding_box = BoundingBoxPainter(painter).bounding_box(
            diagram.get_all_items(), tmpcr
        )
        tmpcr.show_page()
        tmpsurface.flush()

        w, h = bounding_box.width, bounding_box.height
        surface = new_surface(w, h)
        cr = cairo.Context(surface)
        cr.translate(-bounding_box.x, -bounding_box.y)
        painter.paint(items=diagram.get_all_items(), cairo=cr)
        cr.show_page()
        return surface

    def save_svg(self, filename, diagram):
        surface = self.render(diagram, lambda w, h: cairo.SVGSurface(filename, w, h))
        surface.flush()
        surface.finish()

    def save_png(self, filename, diagram):
        surface = self.render(
            diagram,
            lambda w, h: cairo.ImageSurface(
                cairo.FORMAT_ARGB32, int(w + 1), int(h + 1)
            ),
        )
        surface.write_to_png(filename)

    def save_pdf(self, filename, diagram):
        surface = self.render(diagram, lambda w, h: cairo.PDFSurface(filename, w, h))
        surface.flush()
        surface.finish()

    @action(
        name="file-export-svg",
        label=gettext("Export to SVG"),
        tooltip=gettext("Export diagram to SVG"),
    )
    def save_svg_action(self):
        diagram = self.diagrams.get_current_diagram()
        filename = self.save_dialog(
            diagram, gettext("Export diagram to SVG"), "svg", "image/svg+xml"
        )
        if filename:
            self.save_svg(filename, diagram)

    @action(
        name="file-export-png",
        label=gettext("Export to PNG"),
        tooltip=gettext("Export diagram to PNG"),
    )
    def save_png_action(self):
        diagram = self.diagrams.get_current_diagram()
        filename = self.save_dialog(
            diagram, gettext("Export diagram to PNG"), "png", "image/png"
        )
        if filename:
            self.save_png(filename, diagram)

    @action(
        name="file-export-pdf",
        label=gettext("Export to PDF"),
        tooltip=gettext("Export diagram to PDF"),
    )
    def save_pdf_action(self):
        diagram = self.diagrams.get_current_diagram()
        filename = self.save_dialog(
            diagram, gettext("Export diagram to PDF"), "pdf", "application/pdf"
        )
        if filename:
            self.save_pdf(filename, diagram)
