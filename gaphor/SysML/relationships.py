from gaphor.diagram.presentation import LinePresentation, Named, text_name
from gaphor.diagram.shapes import Box, draw_arrow_head
from gaphor.SysML import sysml
from gaphor.UML.compartments import text_stereotypes


class DirectedRelationshipPropertyPathItem(
    Named, LinePresentation[sysml.DirectedRelationshipPropertyPath]
):
    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape_middle=Box(
                text_stereotypes(self, lambda: [self.relation_type]),
                text_name(self),
            ),
        )

        self.draw_head = draw_arrow_head
        self.watch("subject[UML:NamedElement].name").watch(
            "subject[UML:Element].appliedStereotype.classifier.name"
        )

    @property
    def relation_type(self):
        return ""
