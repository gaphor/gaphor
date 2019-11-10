"""Service dedicated to exporting diagrams to a variety of file formats."""

import logging
import os

import cairo
from gaphas.freehand import FreeHandPainter
from gaphas.painter import BoundingBoxPainter, ItemPainter
from gaphas.view import Context, View

from gaphor.abc import ActionProvider, Service
from gaphor.core import _, action
from gaphor.ui.filedialog import FileDialog
from gaphor.ui.questiondialog import QuestionDialog

logger = logging.getLogger(__name__)


def paint(view, cr):
    view.painter.paint(Context(cairo=cr, items=view.canvas.get_all_items(), area=None))


class DiagramExport(Service, ActionProvider):
    """
    Service for exporting diagrams as images (SVG, PNG, PDF).
    """

    def __init__(self, diagrams, properties, export_menu):
        self.diagrams = diagrams
        self.properties = properties
        self.export_menu = export_menu
        export_menu.add_actions(self)

    def shutdown(self):
        self.export_menu.remove_actions(self)

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
        sloppiness = self.properties.get("diagram.sloppiness", 0)

        if sloppiness:
            view.painter = FreeHandPainter(ItemPainter(), sloppiness)
            view.bounding_box_painter = FreeHandPainter(
                BoundingBoxPainter(), sloppiness
            )
        else:
            view.painter = ItemPainter()

    def render(self, canvas, new_surface):
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
        surface = new_surface(w, h)
        cr = cairo.Context(surface)
        view.matrix.translate(-view.bounding_box.x, -view.bounding_box.y)
        paint(view, cr)
        cr.show_page()
        return surface

    def save_svg(self, filename, canvas):
        surface = self.render(canvas, lambda w, h: cairo.SVGSurface(filename, w, h))
        surface.flush()
        surface.finish()

    def save_png(self, filename, canvas):
        surface = self.render(
            canvas,
            lambda w, h: cairo.ImageSurface(
                cairo.FORMAT_ARGB32, int(w + 1), int(h + 1)
            ),
        )
        surface.write_to_png(filename)

    def save_pdf(self, filename, canvas):
        surface = self.render(canvas, lambda w, h: cairo.PDFSurface(filename, w, h))
        surface.flush()
        surface.finish()

    @action(
        name="file-export-svg",
        label=_("Export to SVG"),
        tooltip=_("Export the diagram to SVG"),
    )
    def save_svg_action(self):
        title = _("Export diagram to SVG")
        ext = ".svg"
        diagram = self.diagrams.get_current_diagram()
        filename = self.save_dialog(diagram, title, ext)
        if filename:
            self.save_svg(filename, diagram.canvas)

    @action(
        name="file-export-png",
        label=_("Export to PNG"),
        tooltip=_("Export the diagram to PNG"),
    )
    def save_png_action(self):
        title = _("Export diagram to PNG")
        ext = ".png"
        diagram = self.diagrams.get_current_diagram()
        filename = self.save_dialog(diagram, title, ext)
        if filename:
            self.save_png(filename, diagram.canvas)

    @action(
        name="file-export-pdf",
        label=_("Export to PDF"),
        tooltip=_("Export the diagram to PDF"),
    )
    def save_pdf_action(self):
        title = _("Export diagram to PDF")
        ext = ".pdf"
        diagram = self.diagrams.get_current_diagram()
        filename = self.save_dialog(diagram, title, ext)
        if filename:
            self.save_pdf(filename, diagram.canvas)
