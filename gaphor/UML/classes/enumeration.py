import logging

from gaphor import UML
from gaphor.core import gettext
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import FontStyle, FontWeight, TextAlign, VerticalAlign
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    from_package_str,
)
from gaphor.diagram.shapes import Box, Text, draw_border, draw_top_separator
from gaphor.diagram.support import represents
from gaphor.UML.classes.klass import (
    attribute_watches,
    attributes_compartment,
    operation_watches,
    operations_compartment,
    stereotype_compartments,
    stereotype_watches,
)

log = logging.getLogger(__name__)


@represents(UML.Enumeration)
class EnumerationItem(ElementPresentation[UML.Enumeration], Classified):
    """This item visualizes a Enumeration instance.

    An EnumerationItem contains three compartments:
    1. Enumeration Literals
    2. Attributes
    3. Operations
    """

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id)

        self.watch("show_attributes", self.update_shapes).watch(
            "show_operations", self.update_shapes
        ).watch("show_enumerations", self.update_shapes).watch(
            "subject[NamedElement].name"
        ).watch(
            "subject[NamedElement].namespace.name"
        ).watch(
            "subject[Enumeration].ownedLiteral", self.update_shapes
        ).watch(
            "subject[Enumeration].ownedLiteral.name", self.update_shapes
        )
        attribute_watches(self, "Enumeration")
        operation_watches(self, "Enumeration")
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    show_attributes: attribute[int] = attribute("show_attributes", int, default=True)

    show_operations: attribute[int] = attribute("show_operations", int, default=True)

    show_enumerations: attribute[int] = attribute(
        "show_enumerations", int, default=True
    )

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(
                    text=lambda: UML.recipes.stereotypes_str(
                        self.subject, [gettext("enumeration")]
                    ),
                ),
                Text(
                    text=lambda: self.subject.name or "",
                    style={
                        "font-weight": FontWeight.BOLD,
                        "font-style": FontStyle.ITALIC
                        if self.subject and self.subject.isAbstract
                        else FontStyle.NORMAL,
                    },
                ),
                Text(
                    text=lambda: from_package_str(self),
                    style={"font-size": "x-small"},
                ),
                style={"padding": (12, 4, 12, 4)},
            ),
            *(
                self.show_enumerations
                and self.subject
                and [enumerations_compartment(self.subject)]
                or []
            ),
            *(
                self.show_attributes
                and self.subject
                and [attributes_compartment(self.subject)]
                or []
            ),
            *(
                self.show_operations
                and self.subject
                and [operations_compartment(self.subject)]
                or []
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            style={
                "vertical-align": VerticalAlign.TOP,
            },
            draw=draw_border,
        )


def enumerations_compartment(subject):
    def lazy_format(literal):
        return lambda: format(literal)

    return Box(
        *(
            Text(
                text=lazy_format(literal.name),
                style={
                    "text-align": TextAlign.LEFT,
                },
            )
            for literal in subject.ownedLiteral
        ),
        style={"padding": (4, 4, 4, 4), "min-height": 8},
        draw=draw_top_separator,
    )
