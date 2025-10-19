"""Object node item."""

from gaphor import UML
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, CssNode, IconBox, Text, draw_border
from gaphor.diagram.support import represents
from gaphor.i18n import i18nize
from gaphor.UML.compartments import text_stereotypes

DEFAULT_UPPER_BOUND = "*"

ORDERING_TEXT = {
    "unordered": i18nize("unordered"),
    "ordered": i18nize("ordered"),
    "LIFO": i18nize("LIFO"),
    "FIFO": i18nize("FIFO"),
}


@represents(UML.ObjectNode)
class ObjectNodeItem(Named, ElementPresentation):
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
                    text_stereotypes(self),
                    CssNode("name", self.subject, Text(text=self._format_name)),
                    draw=draw_border,
                ),
                CssNode(
                    "upperbound",
                    None,
                    Text(
                        text=lambda: self.subject.upperBound
                        not in (None, "", DEFAULT_UPPER_BOUND)
                        and f"{{ {diagram.gettext('upperBound')} = {self.subject.upperBound.value} }}"
                        or ""
                    ),
                ),
                CssNode(
                    "ordering",
                    None,
                    Text(
                        text=lambda: self.show_ordering
                        and self.subject.ordering
                        and f"{{ {diagram.gettext('ordering')} = {diagram.gettext(ORDERING_TEXT.get(self.subject.ordering))} }}"
                        or ""
                    ),
                ),
            ),
            width=50,
            height=30,
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject[Element].appliedStereotype.classifier.name")
        self.watch("subject[TypedElement].type.name")
        self.watch("subject[ObjectNode].upperBound")
        self.watch("subject[ObjectNode].ordering")
        self.watch("show_type")
        self.watch("show_ordering")

    show_type: attribute[int] = attribute("show_type", int, default=False)
    show_ordering: attribute[int] = attribute("show_ordering", int, default=False)

    def load(self, name, value):
        if name == "show-ordering":
            name = "show_ordering"
        super().load(name, value)

    def _format_name(self):
        if subject := self.subject:
            if self.show_type and subject.type:
                return f"{subject.name or ''}: {subject.type.name or ''}"
            return subject.name or ""

        return ""
