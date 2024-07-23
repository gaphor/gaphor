from gaphor.C4Model import c4model
from gaphor.diagram.presentation import LinePresentation, Named, text_name
from gaphor.diagram.shapes import Box, CssNode, Text, draw_arrow_head
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes


@represents(
    c4model.C4Dependency,
    head=c4model.C4Dependency.supplier,
    tail=c4model.C4Dependency.client,
)
class C4DependencyItem(Named, LinePresentation[c4model.C4Dependency]):
    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape_middle=Box(
                text_stereotypes(self),
                text_name(self),
                text_technology(self),
            ),
        )

        self._handles[0].pos = (30, 20)
        self._handles[1].pos = (0, 0)

        self.watch("subject")
        self.watch("subject.name")
        self.watch("subject[C4Dependency].technology")
        self.watch("subject.appliedStereotype.classifier.name")

        self.draw_head = draw_arrow_head


def text_technology(item: C4DependencyItem):
    return CssNode(
        "technology",
        item.subject,
        Text(
            text=lambda: item.subject
            and item.subject.technology
            and f"[{item.subject.technology}]"
            or ""
        ),
    )
