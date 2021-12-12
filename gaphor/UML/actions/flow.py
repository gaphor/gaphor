"""Control flow and object flow implementation.

Contains also implementation to split flows using activity edge
connectors.
"""


from gaphor import UML
from gaphor.diagram.presentation import LinePresentation, Named
from gaphor.diagram.shapes import Box, Text, draw_arrow_tail
from gaphor.diagram.support import represents
from gaphor.UML.recipes import stereotypes_str


@represents(UML.ControlFlow)
class FlowItem(LinePresentation, Named):
    """Representation of control flow and object flow.

    Flow item has name and guard. It can be split into two flows with
    activity edge connectors.
    """

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.shape_tail = Box(
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(text=lambda: self.subject.name or ""),
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")

        self.shape_middle = Text(
            text=lambda: self.subject
            and self.subject.guard
            and f"[{self.subject.guard}]"
            or ""
        )

        self.watch("subject[ControlFlow].guard")
        self.watch("subject[ObjectFlow].guard")

        self.draw_tail = draw_arrow_tail
