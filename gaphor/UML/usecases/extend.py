"""Use case extension relationship."""

from gaphor import UML
from gaphor.diagram.presentation import LinePresentation, Named, text_name
from gaphor.diagram.shapes import Box, draw_arrow_head
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes


@represents(UML.Extend, head=UML.Extend.extendedCase, tail=UML.Extend.extension)
class ExtendItem(Named, LinePresentation):
    """Use case extension relationship."""

    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape_middle=Box(
                text_stereotypes(self, lambda: [self.diagram.gettext("extend")]),
                text_name(self),
            ),
        )

        self._handles[0].pos = (30, 20)
        self._handles[1].pos = (0, 0)

        self.watch("subject.appliedStereotype.classifier.name").watch("subject.name")
        self.draw_head = draw_arrow_head
