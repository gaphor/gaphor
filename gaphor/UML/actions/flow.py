"""Control flow and object flow implementation.

Contains also implementation to split flows using activity edge
connectors.
"""


from gaphor import UML
from gaphor.diagram.presentation import LinePresentation, Named, text_name
from gaphor.diagram.shapes import Box, CssNode, Text, draw_arrow_tail
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes


@represents(UML.ControlFlow, head=UML.ControlFlow.source, tail=UML.ControlFlow.target)
class ControlFlowItem(Named, LinePresentation):
    """Representation of control flow.

    Flow item has name and guard. It can be split into two flows with
    activity edge connectors.
    """

    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape_middle=CssNode(
                "guard",
                None,
                Text(
                    text=lambda: self.subject
                    and self.subject.guard
                    and f"[{self.subject.guard}]"
                    or ""
                ),
            ),
            shape_tail=Box(text_stereotypes(self), text_name(self)),
        )

        self.watch("subject.name")
        self.watch("subject.appliedStereotype.classifier.name")

        self.watch("subject[ControlFlow].guard")

        self.draw_tail = draw_arrow_tail


@represents(UML.ObjectFlow, head=UML.ObjectFlow.source, tail=UML.ObjectFlow.target)
class ObjectFlowItem(Named, LinePresentation):
    """Representation of object flow.

    Flow item has name and guard. It can be split into two flows with
    activity edge connectors.
    """

    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape_middle=CssNode(
                "guard",
                None,
                Text(
                    text=lambda: self.subject
                    and self.subject.guard
                    and f"[{self.subject.guard}]"
                    or ""
                ),
            ),
            shape_tail=Box(text_stereotypes(self), text_name(self)),
        )

        self.watch("subject.name")
        self.watch("subject.appliedStereotype.classifier.name")

        self.watch("subject[ObjectFlow].guard")

        self.draw_tail = draw_arrow_tail
