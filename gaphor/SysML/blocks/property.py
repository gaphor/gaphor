"""Property item."""

from typing import Sequence, Union

from gaphor import UML
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import JustifyContent
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, CssNode, Text, draw_border
from gaphor.diagram.support import represents
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches
from gaphor.UML.shapes import text_stereotypes
from gaphor.UML.umlfmt import format_property


@represents(UML.Property)
class PropertyItem(Named, ElementPresentation[UML.Property]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("show_stereotypes", self.update_shapes)
        self.watch("subject[Property].name")
        self.watch("subject[Property].type.name")
        self.watch("subject[Property].lowerValue")
        self.watch("subject[Property].upperValue")
        self.watch("subject[Property].aggregation", self.update_shapes)
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    def justify(self) -> JustifyContent:
        if self.diagram and self.children:
            return JustifyContent.START
        return JustifyContent.CENTER

    def dash(self) -> Sequence[Union[int, float]]:
        if self.subject and self.subject.aggregation != "composite":
            return (7.0, 5.0)
        return ()

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                text_stereotypes(self),
                CssNode(
                    "name",
                    self.subject,
                    Text(
                        text=lambda: format_property(
                            self.subject, type=True, multiplicity=True
                        )
                        or "",
                    ),
                ),
                style={"padding": (12, 4, 12, 4)},
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            style={
                "justify-content": self.justify(),
                "dash-style": self.dash(),
            },
            draw=draw_border,
        )
