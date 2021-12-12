import logging

from gaphor import UML
from gaphor.core import gettext
from gaphor.core.modeling.properties import attribute
from gaphor.core.styling import FontStyle, FontWeight, VerticalAlign
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
    from_package_str,
)
from gaphor.diagram.shapes import Box, Text, draw_border
from gaphor.diagram.support import represents
from gaphor.SysML import sysml
from gaphor.UML.classes.klass import (
    attribute_watches,
    attributes_compartment,
    operation_watches,
    operations_compartment,
    stereotype_compartments,
    stereotype_watches,
)

log = logging.getLogger(__name__)


@represents(UML.DataType)
@represents(UML.PrimitiveType)
@represents(sysml.ValueType)
class DataTypeItem(ElementPresentation[UML.DataType], Classified):
    """This item visualizes a Data Type instance.

    A DataTypeItem contains two compartments:
    1. Attributes
    2. Operations
    """

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id)

        self.watch("show_attributes", self.update_shapes).watch(
            "show_operations", self.update_shapes
        ).watch("subject[NamedElement].name").watch(
            "subject[NamedElement].namespace.name"
        )
        attribute_watches(self, "DataType")
        operation_watches(self, "DataType")
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    show_attributes: attribute[int] = attribute("show_attributes", int, default=True)

    show_operations: attribute[int] = attribute("show_operations", int, default=True)

    def additional_stereotypes(self):
        if isinstance(self.subject, UML.PrimitiveType):
            return [gettext("primitive")]
        elif isinstance(self.subject, sysml.ValueType):
            return [gettext("valueType")]
        elif isinstance(self.subject, UML.DataType):
            return [gettext("dataType")]
        else:
            return ()

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(
                    text=lambda: UML.recipes.stereotypes_str(
                        self.subject, self.additional_stereotypes()
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
