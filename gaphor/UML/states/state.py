"""State diagram item."""


from gaphor import UML
from gaphor.core.styling import TextAlign, VerticalAlign
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, Text, draw_top_separator, stroke
from gaphor.diagram.support import represents
from gaphor.UML.recipes import stereotypes_str


class VertexItem(Named):
    """Abstract class for all vertices.

    All state, pseudostate items derive from VertexItem, which
    simplifies transition connection adapters.
    """


@represents(UML.State)
class StateItem(ElementPresentation[UML.State], VertexItem):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=50, height=30)

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject[State].entry.name", self.update_shapes)
        self.watch("subject[State].exit.name", self.update_shapes)
        self.watch("subject[State].doActivity.name", self.update_shapes)

    def update_shapes(self, event=None):
        compartment = Box(
            Text(
                text=lambda: self.subject.entry.name
                and f"entry / {self.subject.entry.name}"
                or "",
                style={"text-align": TextAlign.LEFT},
            ),
            Text(
                text=lambda: self.subject.exit.name
                and f"exit / {self.subject.exit.name}"
                or "",
                style={"text-align": TextAlign.LEFT},
            ),
            Text(
                text=lambda: self.subject.doActivity.name
                and f"do / {self.subject.doActivity.name}"
                or "",
                style={"text-align": TextAlign.LEFT},
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
                ),
                Text(text=lambda: self.subject.name or ""),
                style={"padding": (4, 4, 4, 4)},
            ),
            compartment,
            style={
                "vertical-align": VerticalAlign.TOP,
            },
            draw=draw_state,
        )


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

    stroke(context)
