import importlib
from typing import Callable, Tuple

import cairo
from gaphas.geometry import Rectangle
from gi.repository import Rsvg

from gaphor.core.modeling import DrawContext
from gaphor.diagram.shapes import Box, cairo_state


def draw_svg_icon(icon: cairo.Surface) -> Callable[[Box, DrawContext, Rectangle], None]:
    def draw_icon(box, context: DrawContext, bounding_box: Rectangle):
        cr = context.cairo
        with cairo_state(cr):
            cr.set_source_surface(icon)
            cr.paint()

    return draw_icon


def load_svg_icon(icon_filename: str) -> Tuple[cairo.Surface, int, int]:
    with importlib.resources.path(
        "gaphor.RAAML.diagram_svgs", icon_filename
    ) as icon_file:
        svg = Rsvg.Handle.new_from_file(str(icon_file))
        dimensions = svg.get_dimensions()
    surface = cairo.RecordingSurface(
        cairo.Content.COLOR_ALPHA,
        cairo.Rectangle(0, 0, dimensions.width, dimensions.height),
    )
    cr = cairo.Context(surface)
    svg.render_cairo(cr)

    return surface, dimensions.width, dimensions.height
