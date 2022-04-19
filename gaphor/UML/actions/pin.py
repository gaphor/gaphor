from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.presentation import AttachedPresentation, Named
from gaphor.diagram.shapes import (
    Box,
    IconBox,
    Text,
    TextAlign,
    VerticalAlign,
    draw_border,
)
from gaphor.diagram.support import represents
from gaphor.UML.recipes import stereotypes_str


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
        self.watch("subject[NamedElement].name")

    def pin_type(self):
        return ""

    def update_shapes(self):
        position = self.connected_side()
        self.update_width(
            self.width,
            factor=0 if position == "left" else 1 if position == "right" else 0.5,
        )
        self.update_height(
            self.width,
            factor=0 if position == "top" else 1 if position == "bottom" else 0.5,
        )

        self.shape = IconBox(
            Box(style={"background-color": (1, 1, 1, 1)}, draw=draw_border),
            Text(
                text=lambda: stereotypes_str(
                    self.subject, [] if self.subject else [self.pin_type()]
                )
            ),
            Text(text=lambda: self.subject and self.subject.name or ""),
            style=text_position(self.connected_side()),
        )


@represents(UML.InputPin)
class InputPinItem(PinItem):
    def pin_type(self):
        return gettext("input pin")


@represents(UML.OutputPin)
class OutputPinItem(PinItem):
    def pin_type(self):
        return gettext("output pin")
