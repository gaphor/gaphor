"""The painter module provides different painters for parts of the diagram.

Painters can be swapped in and out.

Each painter takes care of a layer in the diagram (such as grid, items
and handles).
"""

from __future__ import annotations

from cairo import LINE_JOIN_ROUND
from gaphas.geometry import Rectangle

from gaphor.core.modeling.diagram import DrawContext, StyledDiagram, StyledItem
from gaphor.diagram.diagramlabel import diagram_label
from gaphor.diagram.selection import Selection
from gaphor.diagram.shapes import Box, CssNode, Orientation, Text, cairo_state, stroke
from gaphor.UML.recipes import get_applied_stereotypes, stereotypes_str


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


class DiagramTypePainter:
    def __init__(self, diagram):
        self.diagram = diagram
        self._pentagon = CssNode(
            "pentagon",
            diagram,
            Box(
                CssNode("diagramtype", None, Text(text=lambda: diagram.diagramType)),
                CssNode(
                    "stereotypes", None, Text(text=lambda: stereotypes_str(diagram))
                ),
                CssNode("name", None, Text(text=lambda: diagram_label(diagram))),
                orientation=Orientation.HORIZONTAL,
                draw=draw_pentagon,
            ),
        )

    def paint(self, _items, cr):
        diagram = self.diagram
        if not diagram.diagramType and not any(get_applied_stereotypes(diagram)):
            return

        style = diagram.style(StyledDiagram(diagram))

        context = DrawContext(
            cairo=cr,
            style=style,
            selected=False,
            focused=False,
            hovered=False,
            dropzone=False,
        )

        with cairo_state(cr):
            cr.identity_matrix()

            size = self._pentagon.size(context)  # type: ignore[arg-type]
            bb = Rectangle(0, 0, *size)
            self._pentagon.draw(context, bb)


def draw_pentagon(box, context, bounding_box):
    cr = context.cairo
    w = bounding_box.width
    h = bounding_box.height
    line_width = context.style.get("line-width", 2)
    with cairo_state(cr):
        h2 = h / 2.0
        cr.move_to(-line_width, -line_width)
        cr.line_to(-line_width, h)
        cr.line_to(w - 4, h)
        cr.line_to(w, h2)
        cr.line_to(w, -line_width)
        stroke(context, fill=True)
