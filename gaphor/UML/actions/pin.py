from gaphor import UML
from gaphor.diagram.presentation import AttachedPresentation, Named
from gaphor.diagram.shapes import (
    Box,
    CssNode,
    IconBox,
    Text,
    TextAlign,
    VerticalAlign,
    draw_border,
)
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes
from gaphor.UML.umlfmt import format_pin


def text_position(position):
    return {
        "text-align": TextAlign.LEFT if position == "left" else TextAlign.RIGHT,
        "vertical-align": VerticalAlign.BOTTOM
        if position == "bottom"
        else VerticalAlign.TOP,
    }


class PinItem(Named, AttachedPresentation[UML.Pin]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=16, height=16)
        self.watch("subject.name")
        self.watch("subject[TypedElement].type")
        self.watch("subject[MultiplicityElement].lowerValue")
        self.watch("subject[MultiplicityElement].upperValue")

    def pin_type(self):
        return ""

    def update_shapes(self, event=None):
        side = self.connected_side
        self.update_width(
            self.width,
            factor=0 if side == "left" else 1 if side == "right" else 0.5,
        )
        self.update_height(
            self.width,
            factor=0 if side == "top" else 1 if side == "bottom" else 0.5,
        )

        self.shape = IconBox(
            Box(draw=draw_border),
            text_stereotypes(self, lambda: [] if self.subject else [self.pin_type()]),
            CssNode("name", self.subject, Text(text=lambda: format_pin(self.subject))),
        )


@represents(UML.InputPin)
class InputPinItem(PinItem):
    def pin_type(self):
        return self.diagram.gettext("input pin")


@represents(UML.OutputPin)
class OutputPinItem(PinItem):
    def pin_type(self):
        return self.diagram.gettext("output pin")
