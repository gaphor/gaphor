import logging

from gaphor import UML
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
)
from gaphor.diagram.shapes import Box, CssNode, Text, draw_border, draw_top_separator
from gaphor.diagram.support import represents
from gaphor.UML.classes.klass import (
    attribute_watches,
    attributes_compartment,
    operation_watches,
    operations_compartment,
)
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches
from gaphor.UML.compartments import name_compartment

log = logging.getLogger(__name__)


@represents(UML.Enumeration)
class EnumerationItem(Classified, ElementPresentation[UML.Enumeration]):
    """This item visualizes an Enumeration instance.

    An EnumerationItem contains three compartments:
    1. Enumeration Literals
    2. Attributes
    3. Operations
    """

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id)

        self.watch("show_attributes", self.update_shapes).watch(
            "show_operations", self.update_shapes
        ).watch("show_enumerations", self.update_shapes).watch("subject.name").watch(
            "subject.namespace.name"
        ).watch("subject[Enumeration].ownedLiteral", self.update_shapes).watch(
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

    as_sysml_value_type: attribute[int] = attribute(
        "as_sysml_value_type", int, default=False
    )

    def update_shapes(self, event=None):
        self.shape = Box(
            name_compartment(
                self,
                lambda: [
                    self.diagram.gettext("valueType")
                    if self.as_sysml_value_type
                    else self.diagram.gettext("enumeration")
                ],
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
            draw=draw_border,
        )


def enumerations_compartment(subject):
    def lazy_format(literal):
        return lambda: format(literal)

    return CssNode(
        "compartment",
        subject,
        Box(
            *(
                CssNode(
                    "enumeration",
                    literal,
                    Text(
                        text=lazy_format(literal.name),
                    ),
                )
                for literal in subject.ownedLiteral
            ),
            draw=draw_top_separator,
        ),
    )
