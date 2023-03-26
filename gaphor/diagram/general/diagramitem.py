"""
An item representing a diagram.
"""

from gaphor.core.modeling.diagram import Diagram
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import IconBox, Text, Box, stroke, draw_border
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontWeight


@represents(Diagram)
class DiagramItem(ElementPresentation, Named):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=30, height=30)
        for h in self.handles():
            h.movable = False

        self.shape = IconBox(
            Box(
                Box(draw=draw_diagram),
                style={
                    "padding": (4, 4, 4, 4),
                    "border-radius": 4,
                },
                draw=draw_border,
            ),
            Text(
                text=lambda: self.subject and self.subject.diagramType or "",
                style={
                    "font-weight": FontWeight.BOLD,
                },
            ),
            Text(text=lambda: self.subject and self.subject.name or ""),
        )

        self.watch("subject[Diagram].name")
        self.watch("subject[Diagram].diagramType")


def draw_diagram(box, context, bounding_box):
    cr = context.cairo

    cr.rectangle(5, 13, 8, 12)
    cr.rectangle(18, 5, 8, 12)
    cr.move_to(17, 9)
    cr.line_to(8, 9)
    cr.line_to(8, 12)
    stroke(context)
