import logging

from gaphor import UML
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
)
from gaphor.diagram.shapes import Box, draw_border
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


@represents(UML.DataType)
@represents(UML.PrimitiveType)
class DataTypeItem(Classified, ElementPresentation[UML.DataType]):
    """This item visualizes a Data Type instance.

    A DataTypeItem contains two compartments:
    1. Attributes
    2. Operations
    """

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id)

        self.watch("show_attributes", self.update_shapes).watch(
            "show_operations", self.update_shapes
        ).watch("subject.name").watch("subject.namespace.name")
        attribute_watches(self, "DataType")
        operation_watches(self, "DataType")
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    show_attributes: attribute[int] = attribute("show_attributes", int, default=True)

    show_operations: attribute[int] = attribute("show_operations", int, default=True)

    def additional_stereotypes(self):
        from gaphor.SysML import sysml

        if isinstance(self.subject, UML.PrimitiveType):
            return [self.diagram.gettext("primitive")]
        elif isinstance(self.subject, sysml.ValueType):
            return [self.diagram.gettext("valueType")]
        elif isinstance(self.subject, UML.DataType):
            return [self.diagram.gettext("dataType")]
        return ()

    def update_shapes(self, event=None):
        self.shape = Box(
            name_compartment(self, self.additional_stereotypes),
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
