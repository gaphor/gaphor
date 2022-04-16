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
from gaphor.SysML import sysml
from gaphor.UML.recipes import stereotypes_str


def text_position(position):
    return {
        "text-align": TextAlign.LEFT if position == "left" else TextAlign.RIGHT,
        "vertical-align": VerticalAlign.BOTTOM
        if position == "bottom"
        else VerticalAlign.TOP,
    }


@represents(sysml.ProxyPort)
class ProxyPortItem(Named, AttachedPresentation[sysml.ProxyPort]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=16, height=16)
        self.watch("subject[NamedElement].name")

    def update_shapes(self):
        self.shape = IconBox(
            Box(style={"background-color": (1, 1, 1, 1)}, draw=draw_border),
            Text(text=lambda: stereotypes_str(self.subject, [gettext("proxy")])),
            Text(text=lambda: self.subject and self.subject.name or ""),
            style=text_position(self.connected_side()),
        )
