"""
The painter module provides different painters for parts of the canvas.

Painters can be swapped in and out.

Each painter takes care of a layer in the canvas (such as grid, items
and handles).
"""
from cairo import ANTIALIAS_NONE, LINE_JOIN_ROUND
from gaphas.aspect import PaintFocused
from gaphas.canvas import Context
from gaphas.geometry import Rectangle
from gaphas.painter import CairoBoundingBoxContext, Painter

DEBUG_DRAW_BOUNDING_BOX = False

# The tolerance for Cairo. Bigger values increase speed and reduce accuracy
# (default: 0.1)
TOLERANCE = 0.8


class DrawContext(Context):
    """
    Special context for draw()'ing the item. The draw-context contains
    stuff like the cairo context and properties like selected and
    focused.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ItemPainter(Painter):

    draw_all = False

    def _draw_item(self, item, cairo, area=None):
        view = self.view
        cairo.save()
        try:
            cairo.set_matrix(view.matrix)
            cairo.transform(view.canvas.get_matrix_i2c(item))

            item.draw(
                DrawContext(
                    painter=self,
                    cairo=cairo,
                    _area=area,
                    _item=item,
                    selected=(item in view.selected_items),
                    focused=(item is view.focused_item),
                    hovered=(item is view.hovered_item),
                    dropzone=(item is view.dropzone_item),
                    draw_all=self.draw_all,
                )
            )

        finally:
            cairo.restore()

    def _draw_items(self, items, cairo, area=None):
        """
        Draw the items.
        """
        for item in items:
            self._draw_item(item, cairo, area=area)
            if DEBUG_DRAW_BOUNDING_BOX:
                self._draw_bounds(item, cairo)

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
        self._draw_items(context.items, cairo, context.area)


class BoundingBoxPainter(ItemPainter):
    """
    This specific case of an ItemPainter is used to calculate the
    bounding boxes (in canvas coordinates) for the items.
    """

    draw_all = True

    def _draw_item(self, item, cairo, area=None):
        cairo = CairoBoundingBoxContext(cairo)
        super()._draw_item(item, cairo)
        bounds = cairo.get_bounds()

        # Update bounding box with handles.
        view = self.view
        i2v = view.get_matrix_i2v(item).transform_point
        for h in item.handles():
            cx, cy = i2v(*h.pos)
            bounds += (cx - 5, cy - 5, 9, 9)

        bounds.expand(1)
        view.set_item_bounding_box(item, bounds)

    def _draw_items(self, items, cairo, area=None):
        """
        Draw the items.
        """
        for item in items:
            self._draw_item(item, cairo)

    def paint(self, context):
        self._draw_items(context.items, context.cairo)
