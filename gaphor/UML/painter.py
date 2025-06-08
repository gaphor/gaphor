from __future__ import annotations

from collections.abc import Callable

from gaphas.geometry import Rectangle

from gaphor.core.modeling import StyleSheet
from gaphor.core.modeling.diagram import DrawContext, StyledDiagram
from gaphor.core.styling import Style, StyleNode
from gaphor.diagram.painter import DiagramTypePainter
from gaphor.diagram.shapes import Box, CssNode, Orientation, Text, cairo_state, stroke
from gaphor.UML.recipes import get_applied_stereotypes, stereotypes_str
from gaphor.UML.uml import Diagram


@DiagramTypePainter.register(Diagram)  # type: ignore[attr-defined]
class UMLDiagramTypePainter:
    def __init__(
        self,
        diagram: Diagram,
        compute_style: Callable[[StyleNode], Style] | None = None,
    ):
        self.diagram = diagram
        self.compute_style: Callable[[StyleNode], Style] = (
            compute_style or StyleSheet().compute_style
        )
        self._pentagon = CssNode(
            "pentagon",
            diagram,
            Box(
                CssNode("diagramtype", None, Text(text=lambda: diagram.diagramType)),
                CssNode(
                    "stereotypes", None, Text(text=lambda: stereotypes_str(diagram))
                ),
                CssNode("name", None, Text(text=lambda: self.label())),
                orientation=Orientation.HORIZONTAL,
                draw=draw_pentagon,
            ),
        )

    def label(self):
        return self.diagram.name

    def paint(self, _items, cr):
        diagram = self.diagram
        if not diagram.diagramType and not any(get_applied_stereotypes(diagram)):
            return

        context = DrawContext(
            cairo=cr,
            style=self.compute_style(StyledDiagram(diagram)),
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
