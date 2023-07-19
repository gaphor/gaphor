"""Service dedicated to exporting diagrams to a variety of file formats."""

import re

import cairo
from gaphas.painter import BoundingBoxPainter, FreeHandPainter, PainterChain

from gaphor.core.modeling.diagram import StyledDiagram
from gaphor.diagram.painter import DiagramTypePainter, ItemPainter


def escape_filename(diagram_name):
    return re.sub("\\W+", "_", diagram_name)


def render(
    diagram, modeling_language, new_surface, padding=8, write_to_png=None
) -> None:
    diagram.update_now(diagram.get_all_items())

    painter = new_painter(diagram, modeling_language)

    # Update bounding boxes with a temporary Cairo Context
    # (used for stuff like calculating font metrics)
    bounding_box = calc_bounding_box(diagram, painter)
    type_padding = diagram_type_height(diagram, modeling_language)

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


def diagram_type_height(diagram, modeling_language):
    if not diagram.diagramType:
        return 0

    bounding_box = calc_bounding_box(
        diagram, DiagramTypePainter(diagram, modeling_language)
    )

    return bounding_box.height


def calc_bounding_box(diagram, painter):
    with cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0) as tmpsurface:
        tmpcr = cairo.Context(tmpsurface)
        bounding_box = BoundingBoxPainter(painter).bounding_box(
            diagram.get_all_items(), tmpcr
        )
        tmpcr.show_page()
        tmpsurface.flush()
    return bounding_box


def save_svg(filename, diagram, modeling_language):
    render(diagram, modeling_language, lambda w, h: cairo.SVGSurface(filename, w, h))


def save_png(filename, diagram, modeling_language):
    render(
        diagram,
        modeling_language,
        lambda w, h: cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w + 1), int(h + 1)),
        write_to_png=filename,
    )


def save_pdf(filename, diagram, modeling_language):
    render(diagram, modeling_language, lambda w, h: cairo.PDFSurface(filename, w, h))


def save_eps(filename, diagram, modeling_language):
    def new_surface(w, h):
        surface = cairo.PSSurface(filename, w, h)
        surface.set_eps(True)
        return surface

    render(diagram, modeling_language, new_surface)


def new_painter(diagram, modeling_language):
    style = diagram.style(StyledDiagram(diagram))
    sloppiness = style.get("line-style", 0.0)
    item_painter = (
        FreeHandPainter(ItemPainter(), sloppiness) if sloppiness else ItemPainter()
    )
    return (
        PainterChain()
        .append(item_painter)
        .append(DiagramTypePainter(diagram, modeling_language))
    )
