"""The painter module provides different painters for parts of the diagram.

Painters can be swapped in and out.

Each painter takes care of a layer in the diagram (such as grid, items
and handles).
"""

from __future__ import annotations

from typing import Optional

from cairo import LINE_JOIN_ROUND

from gaphor.core.modeling.diagram import DrawContext, StyledItem
from gaphor.diagram.selection import Selection

# The tolerance for Cairo. Bigger values increase speed and reduce accuracy
# (default: 0.1)
TOLERANCE = 0.8


class ItemPainter:
    def __init__(self, selection: Optional[Selection] = None):
        self.selection: Selection = selection or Selection()

    def paint_item(self, item, cairo):
        selection = self.selection
        diagram = item.diagram
        style = diagram.style(StyledItem(item, selection))
        cairo.push_group()
        try:
            cairo.set_source_rgba(*style["color"])
            cairo.transform(item.matrix_i2c.to_cairo())

            item.draw(
                DrawContext(
                    cairo=cairo,
                    style=style,
                    selected=(item in selection.selected_items),
                    focused=(item is selection.focused_item),
                    hovered=(item is selection.hovered_item),
                    dropzone=(item is selection.dropzone_item),
                )
            )

        finally:
            cairo.pop_group_to_source()
            cairo.paint_with_alpha(0.4 if item in selection.grayed_out_items else 1.0)

    def paint(self, items, cairo):
        """Draw the items."""
        cairo.set_tolerance(TOLERANCE)
        cairo.set_line_join(LINE_JOIN_ROUND)
        for item in items:
            self.paint_item(item, cairo)
