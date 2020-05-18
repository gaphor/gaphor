"""
The painter module provides different painters for parts of the canvas.

Painters can be swapped in and out.

Each painter takes care of a layer in the canvas (such as grid, items
and handles).
"""
from dataclasses import dataclass

from cairo import ANTIALIAS_NONE, LINE_JOIN_ROUND
from cairo import Context as CairoContext
from gaphas.aspect import PaintFocused
from gaphas.canvas import Context
from gaphas.geometry import Rectangle
from gaphas.painter import CairoBoundingBoxContext, Painter

DEBUG_DRAW_BOUNDING_BOX = False

# The tolerance for Cairo. Bigger values increase speed and reduce accuracy
# (default: 0.1)
TOLERANCE = 0.8


@dataclass(frozen=True)
class DrawContext:
    """
    Special context for draw()'ing the item. The draw-context contains
    stuff like the cairo context and flags like selected and
    focused.
    """

    painter: Painter
    cairo: CairoContext
    selected: bool
    focused: bool
    hovered: bool
    dropzone: bool
    draw_all: bool


class ItemPainter(Painter):
    def draw_item(self, item, cairo, draw_all=False):
        view = self.view
        cairo.save()
        try:
            cairo.set_matrix(view.matrix)
            cairo.transform(view.canvas.get_matrix_i2c(item))

            item.draw(
                DrawContext(
                    painter=self,
                    cairo=cairo,
                    selected=(item in view.selected_items),
                    focused=(item is view.focused_item),
                    hovered=(item is view.hovered_item),
                    dropzone=(item is view.dropzone_item),
                    draw_all=draw_all,
                )
            )

        finally:
            cairo.restore()

    def _draw_bounds(self, item, cairo):
        view = self.view
        try:
            b = view.get_item_bounding_box(item)
        except KeyError:
            pass  # No bounding box right now..
        else:
            cairo.save()
            cairo.identity_matrix()
            cairo.set_source_rgb(0.8, 0, 0)
            cairo.set_line_width(1.0)
            cairo.rectangle(*b)
            cairo.stroke()
            cairo.restore()

    def paint(self, context):
        cairo = context.cairo
        cairo.set_tolerance(TOLERANCE)
        cairo.set_line_join(LINE_JOIN_ROUND)
        for item in context.items:
            self.draw_item(item, cairo)
            if DEBUG_DRAW_BOUNDING_BOX:
                self._draw_bounds(item, cairo)


class BoundingBoxPainter(Painter):
    """
    This specific case of an ItemPainter is used to calculate the
    bounding boxes (in canvas coordinates) for the items.
    """

    def __init__(self, item_painter, view=None):
        super().__init__(view)
        self.item_painter = item_painter

    def draw_item(self, item, cairo):
        cairo = CairoBoundingBoxContext(cairo)
        self.item_painter.draw_item(item, cairo, draw_all=True)
        bounds = cairo.get_bounds()

        # Update bounding box with handles.
        view = self.view
        i2v = view.get_matrix_i2v(item).transform_point
        for h in item.handles():
            cx, cy = i2v(*h.pos)
            bounds += (cx - 5, cy - 5, 9, 9)

        bounds.expand(1)
        view.set_item_bounding_box(item, bounds)

    def paint(self, context):
        cairo = context.cairo
        for item in context.items:
            self.draw_item(item, cairo)
