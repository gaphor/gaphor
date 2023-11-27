from gaphor.diagram.presentation import LinePresentation, Named
from gaphor.diagram.shapes import Box, Text, draw_arrow_head
from gaphor.UML.recipes import stereotypes_str


class DirectedRelationshipPropertyPathItem(Named, LinePresentation):
    relation_type = ""

    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape_middle=Box(
                Text(
                    text=lambda: stereotypes_str(self.subject, (self.relation_type,)),
                ),
                Text(text=lambda: self.subject.name or ""),
            ),
            style={"dash-style": (7.0, 5.0)},
        )

        self.draw_head = draw_arrow_head
        self.watch("subject[NamedElement].name").watch(
            "subject.appliedStereotype.classifier.name"
        )
