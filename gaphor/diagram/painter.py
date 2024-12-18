"""The painter module provides different painters for parts of the diagram.

Painters can be swapped in and out.

Each painter takes care of a layer in the diagram (such as grid, items
and handles).
"""

from __future__ import annotations

from functools import singledispatch

from cairo import LINE_JOIN_ROUND

from gaphor.core.modeling.diagram import Diagram, DrawContext, StyledItem
from gaphor.diagram.selection import Selection


class ItemPainter:
    def __init__(
        self, selection: Selection | None = None, dark_mode: bool | None = None
    ):
        self.selection: Selection = selection or Selection()
        self.dark_mode = dark_mode

    def paint_item(self, item, cr):
        selection = self.selection
        if not (diagram := item.diagram):
            return

        style = diagram.style(StyledItem(item, selection, self.dark_mode))

        cr.save()
        try:
            cr.set_line_join(LINE_JOIN_ROUND)
            cr.set_source_rgba(*style["color"])
            cr.transform(item.matrix_i2c.to_cairo())

            item.draw(
                DrawContext(
                    cairo=cr,
                    style=style,
                    selected=(item in selection.selected_items),
                    focused=(item is selection.focused_item),
                    hovered=(item is selection.hovered_item),
                    dropzone=(item is selection.dropzone_item),
                )
            )

        finally:
            cr.restore()

    def paint(self, items, cr):
        """Draw the items."""
        for item in items:
            self.paint_item(item, cr)


@singledispatch
class DiagramTypePainter:
    """Diagram painter.

    Allows for drawing diagram specific admonitions,
    such as is common for UML and SysML diagrams.
    """

    def __init__(self, _diagram: Diagram):
        pass

    def paint(self, _items, _cr):
        pass
