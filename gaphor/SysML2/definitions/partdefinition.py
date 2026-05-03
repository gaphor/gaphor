"""PartDefinition diagram item."""

from gaphor.diagram.presentation import ElementPresentation
from gaphor.diagram.shapes import Box, CssNode, Text, draw_border
from gaphor.diagram.support import represents
from gaphor.SysML2 import sysml2


@represents(sysml2.PartDefinition)
class PartDefinitionItem(ElementPresentation[sysml2.PartDefinition]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)
        self.update_shapes()
        self.watch("subject[KerML:Element].declaredName")

    def update_shapes(self, event=None):
        self.shape = Box(
            CssNode(
                "compartment",
                None,
                Box(
                    CssNode(
                        "stereotypes",
                        None,
                        Text(text=lambda: "«part def»"),
                    ),
                    CssNode(
                        "name",
                        self.subject,
                        Text(
                            text=lambda: (
                                self.subject and self.subject.declaredName or ""
                            )
                        ),
                    ),
                ),
            ),
            draw=draw_border,
        )
