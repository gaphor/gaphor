from gaphor import UML
from gaphor.diagram.presentation import Classified, ElementPresentation
from gaphor.diagram.shapes import Box, Text, TextAlign, VerticalAlign, draw_border
from gaphor.diagram.support import represents
from gaphor.UML.recipes import stereotypes_str


@represents(UML.Activity)
class ActivityItem(Classified, ElementPresentation):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=50, height=30)

        self.width = 100
        self.shape = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
                style={"text-align": TextAlign.LEFT},
            ),
            Text(
                text=lambda: self.subject.name or "",
                style={"text-align": TextAlign.LEFT},
            ),
            style={
                "padding": (4, 12, 4, 12),
                "border-radius": 20,
                "vertical-align": VerticalAlign.TOP,
            },
            draw=draw_border,
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")
