"""
State diagram item.
"""

import operator

from gaphor import UML
from gaphor.UML.modelfactory import stereotypes_str
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, EditableText, Text, draw_top_separator
from gaphor.diagram.text import TextAlign, VerticalAlign
from gaphor.diagram.support import represents


class VertexItem(Named):
    """
    Abstract class for all vertices. All state, pseudostate items derive
    from VertexItem, which simplifies transition connection adapters.
    """

    pass


@represents(UML.State)
class StateItem(ElementPresentation, VertexItem):
    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        self.update_shapes()

        self.watch("subject<NamedElement>.name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject<State>.entry.name", self.update_shapes)
        self.watch("subject<State>.exit.name", self.update_shapes)
        self.watch("subject<State>.doActivity.name", self.update_shapes)

    def update_shapes(self, event=None):
        compartment = Box(
            Text(
                text=lambda: self.subject.entry.name
                and f"entry / {self.subject.entry.name}"
                or "",
                style={"text-align": TextAlign.LEFT, "min-height": 0},
            ),
            Text(
                text=lambda: self.subject.exit.name
                and f"exit / {self.subject.exit.name}"
                or "",
                style={"text-align": TextAlign.LEFT, "min-height": 0},
            ),
            Text(
                text=lambda: self.subject.doActivity.name
                and f"do / {self.subject.doActivity.name}"
                or "",
                style={"text-align": TextAlign.LEFT, "min-height": 0},
            ),
            style={"padding": (4, 4, 4, 4), "vertical-align": VerticalAlign.TOP},
            draw=draw_top_separator,
        )
        if not any(t.text() for t in compartment.children):
            compartment = Box()

        self.shape = Box(
            Box(
                Text(
                    text=lambda: stereotypes_str(self.subject),
                    style={"min-width": 0, "min-height": 0},
                ),
                EditableText(text=lambda: self.subject.name or ""),
                style={"padding": (4, 4, 4, 4)},
            ),
            compartment,
            style={
                "min-width": 50,
                "min-height": 30,
                "vertical-align": VerticalAlign.TOP,
            },
            draw=draw_state,
        )
        self.request_update()

    def postload(self):
        super().postload()
        self.update_shapes()


def draw_state(box, context, bounding_box):
    cr = context.cairo
    dx = 15
    dy = 8
    ddx = 0.4 * dx
    ddy = 0.4 * dy
    width = bounding_box.width
    height = bounding_box.height

    cr.move_to(0, dy)
    cr.curve_to(0, ddy, ddx, 0, dx, 0)
    cr.line_to(width - dx, 0)
    cr.curve_to(width - ddx, 0, width, ddy, width, dy)
    cr.line_to(width, height - dy)
    cr.curve_to(width, height - ddy, width - ddx, height, width - dx, height)
    cr.line_to(dx, height)
    cr.curve_to(ddx, height, 0, height - ddy, 0, height - dy)
    cr.close_path()

    cr.stroke()
