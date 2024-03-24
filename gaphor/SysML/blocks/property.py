"""Property item."""


from gaphor import UML
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, CssNode, Text, draw_border
from gaphor.diagram.support import represents
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches
from gaphor.UML.compartments import text_stereotypes
from gaphor.UML.umlfmt import format_property


@represents(UML.Property)
class PropertyItem(Named, ElementPresentation[UML.Property]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("show_stereotypes", self.update_shapes)
        self.watch("subject[Property].name")
        self.watch("subject[Property].type.name")
        self.watch("subject[Property].typeValue")
        self.watch("subject[Property].lowerValue")
        self.watch("subject[Property].upperValue")
        self.watch("subject[Property].aggregation", self.update_shapes)
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    def update_shapes(self, event=None):
        self.shape = Box(
            CssNode(
                "compartment",
                None,
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
                ),
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            draw=draw_border,
        )
