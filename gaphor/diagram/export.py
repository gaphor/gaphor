"""Service dedicated to exporting diagrams to a variety of file formats."""

import re

import cairo
from gaphas.geometry import Rectangle
from gaphas.painter import FreeHandPainter, PainterChain

from gaphor.core.modeling.diagram import StyledDiagram
from gaphor.diagram.painter import DiagramTypePainter, ItemPainter


def escape_filename(diagram_name):
    return re.sub("\\W+", "_", diagram_name)


def render(diagram, new_surface, padding=8, write_to_png=None) -> None:
    diagram.update(diagram.ownedPresentation)

    painter = new_painter(diagram)

    # Update bounding boxes with a temporary Cairo Context
    # (used for stuff like calculating font metrics)
    bounding_box = calc_bounding_box(diagram, painter)
    type_padding = diagram_type_height(diagram)

    w, h = (
        bounding_box.width + 2 * padding,
        bounding_box.height + 2 * padding + type_padding,
    )

    with new_surface(w, h) as surface:
        cr = cairo.Context(surface)

        bg_color = diagram.style(StyledDiagram(diagram)).get("background-color")
        if bg_color and bg_color[3]:
            cr.rectangle(0, 0, w, h)
            cr.set_source_rgba(*bg_color)
            cr.fill()

        cr.translate(
            -bounding_box.x + padding, -bounding_box.y + padding + type_padding
        )
        painter.paint(diagram.get_all_items(), cr)
        cr.show_page()

        if write_to_png:
            surface.write_to_png(write_to_png)


def diagram_type_height(diagram):
    if not diagram.diagramType:
        return 0

    bounding_box = calc_bounding_box(diagram, DiagramTypePainter(diagram))

    return bounding_box.height


def calc_bounding_box(diagram, painter):
    surface = cairo.RecordingSurface(cairo.Content.COLOR_ALPHA, None)
    cr = cairo.Context(surface)
    painter.paint(diagram.get_all_items(), cr)
    return Rectangle(*surface.ink_extents())


def save_svg(filename, diagram):
    render(diagram, lambda w, h: cairo.SVGSurface(filename, w, h))


def save_png(filename, diagram):
    render(
        diagram,
        lambda w, h: cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w + 1), int(h + 1)),
        write_to_png=filename,
    )


def save_pdf(filename, diagram):
    render(diagram, lambda w, h: cairo.PDFSurface(filename, w, h))


def save_eps(filename, diagram):
    def new_surface(w, h):
        surface = cairo.PSSurface(filename, w, h)
        surface.set_eps(True)
        return surface

    render(diagram, new_surface)


def new_painter(diagram):
    style = diagram.style(StyledDiagram(diagram))
    sloppiness = style.get("line-style", 0.0)
    item_painter = (
        FreeHandPainter(ItemPainter(), sloppiness) if sloppiness else ItemPainter()
    )
    return PainterChain().append(item_painter).append(DiagramTypePainter(diagram))
