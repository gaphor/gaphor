from gaphor.diagram.presentation import LinePresentation, Named
from gaphor.diagram.shapes import Box, Text, draw_arrow_head
from gaphor.UML.shapes import text_stereotypes


class DirectedRelationshipPropertyPathItem(Named, LinePresentation):
    relation_type = ""

    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape_middle=Box(
                text_stereotypes(self, lambda: [self.relation_type]),
                Text(text=lambda: self.subject.name or ""),
            ),
            style={"dash-style": (7.0, 5.0)},
        )

        self.draw_head = draw_arrow_head
        self.watch("subject[NamedElement].name").watch(
            "subject.appliedStereotype.classifier.name"
        )
