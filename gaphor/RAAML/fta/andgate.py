"""AND gate item definition."""

from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    from_package_str,
)
from gaphor.diagram.shapes import Box, EditableText, IconBox, Text
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontStyle, FontWeight
from gaphor.RAAML import raaml
from gaphor.RAAML.fta.svgicon import draw_svg_icon, load_svg_icon
from gaphor.UML.modelfactory import stereotypes_str

ICON, WIDTH, HEIGHT = load_svg_icon("and.svg")


@represents(raaml.AND)
class ANDItem(ElementPresentation, Classified):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=WIDTH, height=HEIGHT)

        for handle in self.handles():
            handle.movable = False

        self.watch("subject[NamedElement].name").watch(
            "subject[NamedElement].namespace.name"
        )

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(draw=draw_svg_icon(ICON)),
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            EditableText(
                text=lambda: self.subject.name or "",
                style={
                    "font-weight": FontWeight.BOLD,
                    "font-style": FontStyle.NORMAL,
                },
            ),
            Text(
                text=lambda: from_package_str(self),
                style={"font-size": "x-small"},
            ),
        )
