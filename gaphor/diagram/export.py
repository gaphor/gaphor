"""Service dedicated to exporting diagrams to a variety of file formats."""

import contextlib
import re
from typing import NamedTuple

import cairo
from gaphas.geometry import Rectangle
from gaphas.painter import FreeHandPainter, PainterChain

from gaphor.core.modeling import StyleSheet
from gaphor.core.modeling.diagram import Diagram, StyledDiagram
from gaphor.diagram.painter import DiagramTypePainter, ItemPainter


class RenderContext(NamedTuple):
    """Pre-computed rendering state for a diagram."""

    items: list
    painter: PainterChain
    style_sheet: StyleSheet
    bounding_box: Rectangle
    type_padding: float

    def get_offsets(self, padding) -> tuple[float, float]:
        return (
            -self.bounding_box.x + padding,
            -self.bounding_box.y + padding + self.type_padding,
        )


def escape_filename(diagram_name):
    return re.sub("\\W+", "_", diagram_name)


def _prepare_render(
    diagram: Diagram, items=None, with_diagram_type: bool = True
) -> RenderContext:
    """Set up painter chain and compute bounding box for a diagram.

    Shared preparation logic used by both render() and
    diagram_render_offsets().
    """
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

    return RenderContext(
        items=items,
        painter=painter,
        style_sheet=style_sheet,
        bounding_box=bounding_box,
        type_padding=type_padding,
    )


def render(
    diagram: Diagram, new_surface, items=None, with_diagram_type=True, padding=8
) -> None:
    ctx = _prepare_render(diagram, items, with_diagram_type)

    w, h = (
        ctx.bounding_box.width + 2 * padding,
        ctx.bounding_box.height + 2 * padding + ctx.type_padding,
    )

    with new_surface(w, h) as surface:
        cr = cairo.Context(surface)

        bg_color = ctx.style_sheet.compute_style(StyledDiagram(diagram)).get(
            "background-color"
        )
        if bg_color and bg_color[3]:
            cr.rectangle(0, 0, w, h)
            cr.set_source_rgba(*bg_color)
            cr.fill()

        cr.translate(*ctx.get_offsets(padding))
        ctx.painter.paint(ctx.items, cr)
        cr.show_page()
        surface.flush()


def diagram_render_offsets(diagram: Diagram, padding: int = 8) -> tuple[float, float]:
    """Return the (tx, ty) translation offset applied during diagram export.

    Useful for post-processing exported files, e.g. injecting clickable
    overlay regions whose coordinates must match the exported SVG.
    """
    ctx = _prepare_render(diagram)
    return ctx.get_offsets(padding)


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
