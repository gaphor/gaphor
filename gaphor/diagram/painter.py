"""The painter module provides different painters for parts of the canvas.

Painters can be swapped in and out.

Each painter takes care of a layer in the canvas (such as grid, items
and handles).
"""

from __future__ import annotations

from typing import Optional

from cairo import LINE_JOIN_ROUND
from gaphas.view import Selection

from gaphor.core.modeling.diagram import DrawContext, StyledItem

DEBUG_DRAW_BOUNDING_BOX = False

# The tolerance for Cairo. Bigger values increase speed and reduce accuracy
# (default: 0.1)
TOLERANCE = 0.8


class ItemPainter:
    def __init__(self, selection: Optional[Selection] = None):
        self.selection: Selection = selection if selection else Selection()

    def paint_item(self, item, cairo):
        selection = self.selection
        diagram = item.diagram
        cairo.save()
        try:
            cairo.transform(item.matrix_i2c.to_cairo())

            selection = self.selection

            item.draw(
                DrawContext(
                    cairo=cairo,
                    style=diagram.style(StyledItem(item, selection)),
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
