"""Service dedicated to exporting diagrams to a variety of file formats."""

import contextlib
import re

import cairo
from gaphas.geometry import Rectangle
from gaphas.painter import FreeHandPainter, PainterChain

from gaphor.core.modeling import StyleSheet
from gaphor.core.modeling.diagram import Diagram, StyledDiagram
from gaphor.diagram.painter import DiagramTypePainter, ItemPainter


def escape_filename(diagram_name):
    return re.sub("\\W+", "_", diagram_name)


def render(
    diagram: Diagram, new_surface, items=None, with_diagram_type=True, padding=8
) -> None:
    if items is None:
        items = list(diagram.get_all_items())

    diagram.update(diagram.ownedPresentation)
    model = diagram.model
    style_sheet = model.style_sheet or StyleSheet()
    item_painter = ItemPainter(compute_style=style_sheet.compute_style)
    sloppiness = style_sheet.compute_style(StyledDiagram(diagram)).get(
        "line-style", 0.0
    )
    painter = PainterChain().append(
        FreeHandPainter(item_painter, sloppiness) if sloppiness else item_painter
    )

    if with_diagram_type:
        painter.append(DiagramTypePainter(diagram, style_sheet.compute_style))
        type_padding = diagram_type_height(diagram)
    else:
        type_padding = 0

    # Update bounding boxes with a temporary Cairo Context
    # (used for stuff like calculating font metrics)
    bounding_box = calc_bounding_box(items, painter)

    w, h = (
        bounding_box.width + 2 * padding,
        bounding_box.height + 2 * padding + type_padding,
    )

    with new_surface(w, h) as surface:
        cr = cairo.Context(surface)

        bg_color = style_sheet.compute_style(StyledDiagram(diagram)).get(
            "background-color"
        )
        if bg_color and bg_color[3]:
            cr.rectangle(0, 0, w, h)
            cr.set_source_rgba(*bg_color)
            cr.fill()

        cr.translate(
            -bounding_box.x + padding, -bounding_box.y + padding + type_padding
        )
        painter.paint(items, cr)
        cr.show_page()
        surface.flush()


def diagram_type_height(diagram):
    if not diagram.diagramType:
        return 0

    bounding_box = calc_bounding_box(
        diagram.get_all_items(), DiagramTypePainter(diagram)
    )

    return bounding_box.height


def calc_bounding_box(items, painter):
    surface = cairo.RecordingSurface(cairo.Content.COLOR_ALPHA, None)
    cr = cairo.Context(surface)
    painter.paint(items, cr)
    return Rectangle(*surface.ink_extents())


def save_svg(filename, diagram):
    render(diagram, lambda w, h: cairo.SVGSurface(filename, w, h))


def save_png(filename, diagram):
    @contextlib.contextmanager
    def new_png_surface(w, h):
        with cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w + 1), int(h + 1)) as surface:
            yield surface
            surface.write_to_png(filename)

    render(
        diagram,
        new_png_surface,
    )


def save_pdf(filename, diagram):
    render(diagram, lambda w, h: cairo.PDFSurface(filename, w, h))


def save_eps(filename, diagram):
    def new_surface(w, h):
        surface = cairo.PSSurface(filename, w, h)
        surface.set_eps(True)
        return surface

    render(diagram, new_surface)
