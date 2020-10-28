"""The painter module provides different painters for parts of the canvas.

Painters can be swapped in and out.

Each painter takes care of a layer in the canvas (such as grid, items
and handles).
"""

from __future__ import annotations

from cairo import LINE_JOIN_ROUND
from gaphas.view import GtkView, Selection

from gaphor.core.modeling.diagram import DrawContext, StyledItem

DEBUG_DRAW_BOUNDING_BOX = False

# The tolerance for Cairo. Bigger values increase speed and reduce accuracy
# (default: 0.1)
TOLERANCE = 0.8


class ItemPainter:
    def __init__(self, view):
        self.view = view

    def paint_item(self, item, cairo):
        view = self.view
        diagram = item.diagram
        cairo.save()
        try:
            cairo.set_matrix(view.matrix.to_cairo())
            cairo.transform(view.canvas.get_matrix_i2c(item).to_cairo())

            selection = view.selection if isinstance(view, GtkView) else Selection()

            item.draw(
                DrawContext(
                    cairo=cairo,
                    style=diagram.style(StyledItem(item, view)),
                    selected=(item in selection.selected_items),
                    focused=(item is selection.focused_item),
                    hovered=(item is selection.hovered_item),
                    dropzone=(item is selection.dropzone_item),
                )
            )

        finally:
            cairo.restore()

    def paint(self, items, cairo):
        """Draw the items."""
        cairo.set_tolerance(TOLERANCE)
        cairo.set_line_join(LINE_JOIN_ROUND)
        for item in items:
            self.paint_item(item, cairo)
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
