"""Object node item."""

from gaphor import UML
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, EditableText, IconBox, Text, draw_border
from gaphor.diagram.support import represents
from gaphor.UML.modelfactory import stereotypes_str

DEFAULT_UPPER_BOUND = "*"


@represents(UML.ObjectNode)
class ObjectNodeItem(ElementPresentation, Named):
    """Representation of object node. Object node is ordered and has upper
    bound specification.

    Ordering information can be hidden by user.
    """

    def __init__(self, diagram, id=None):
        super().__init__(
            diagram,
            id,
            shape=IconBox(
                Box(
                    Text(
                        text=lambda: stereotypes_str(self.subject),
                    ),
                    EditableText(text=lambda: self.subject.name or ""),
                    style={
                        "min-width": 50,
                        "min-height": 30,
                        "padding": (5, 10, 5, 10),
                    },
                    draw=draw_border,
                ),
                Text(
                    text=lambda: self.subject.upperBound
                    not in (None, "", DEFAULT_UPPER_BOUND)
                    and f"{{ upperBound = {self.subject.upperBound} }}"
                    or "",
                ),
                Text(
                    text=lambda: self.show_ordering
                    and self.subject.ordering
                    and f"{{ ordering = {self.subject.ordering} }}"
                    or "",
                ),
            ),
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject[ObjectNode].upperBound")
        self.watch("subject[ObjectNode].ordering")
        self.watch("show_ordering")

    show_ordering: attribute[bool] = attribute("show_ordering", bool, False)

    def load(self, name, value):
        if name == "show-ordering":
            name = "show_ordering"
        super().load(name, value)
