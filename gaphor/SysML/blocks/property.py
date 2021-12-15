"""Property item."""

from typing import Sequence, Union

from gaphor import UML
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import FontWeight, VerticalAlign
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, Text, draw_border
from gaphor.diagram.support import represents
from gaphor.UML.classes.stereotype import stereotype_compartments
from gaphor.UML.umlfmt import format_property


@represents(UML.Property)
class PropertyItem(ElementPresentation[UML.Property], Named):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("show_stereotypes", self.update_shapes)
        self.watch("subject[Property].name")
        self.watch("subject[Property].type.name")
        self.watch("subject[Property].lowerValue")
        self.watch("subject[Property].upperValue")
        self.watch("subject.appliedStereotype", self.update_shapes)
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject.appliedStereotype.slot", self.update_shapes)
        self.watch("subject.appliedStereotype.slot.definingFeature.name")
        self.watch("subject.appliedStereotype.slot.value", self.update_shapes)
        self.watch("subject[Property].aggregation", self.update_shapes)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    def alignment(self) -> VerticalAlign:
        if self.diagram and self.children:
            return VerticalAlign.TOP
        else:
            return VerticalAlign.MIDDLE

    def dash(self) -> Sequence[Union[int, float]]:
        if self.subject and self.subject.aggregation != "composite":
            return (7.0, 5.0)
        else:
            return ()

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(
                    text=lambda: UML.recipes.stereotypes_str(self.subject),
                ),
                Text(
                    text=lambda: format_property(
                        self.subject, type=True, multiplicity=True
                    )
                    or "",
                    style={"font-weight": FontWeight.BOLD},
                ),
                style={"padding": (12, 4, 12, 4)},
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            style={
                "vertical-align": self.alignment(),
                "dash-style": self.dash(),
            },
            draw=draw_border
        )
