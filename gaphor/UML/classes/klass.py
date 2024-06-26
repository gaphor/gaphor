import logging

from gaphor import UML
from gaphor.core.format import format
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
)
from gaphor.diagram.shapes import Box, CssNode, Text, draw_border, draw_top_separator
from gaphor.diagram.support import represents
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches
from gaphor.UML.compartments import name_compartment

log = logging.getLogger(__name__)


@represents(UML.Class)
@represents(UML.Stereotype)
class ClassItem(Classified, ElementPresentation[UML.Class]):
    """This item visualizes a Class instance.

    A ClassItem contains two compartments: one for attributes and one
    for operations.
    """

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id)

        self.watch("show_stereotypes", self.update_shapes).watch(
            "show_attributes", self.update_shapes
        ).watch("show_operations", self.update_shapes).watch("subject.name").watch(
            "subject.namespace.name"
        ).watch("subject[Classifier].isAbstract", self.update_shapes)
        attribute_watches(self, "Class")
        operation_watches(self, "Class")
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    show_attributes: attribute[int] = attribute("show_attributes", int, default=True)

    show_operations: attribute[int] = attribute("show_operations", int, default=True)

    def additional_stereotypes(self):
        if isinstance(self.subject, UML.Stereotype):
            return [self.diagram.gettext("stereotype")]
        elif UML.recipes.is_metaclass(self.subject):
            return [self.diagram.gettext("metaclass")]
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


def attribute_watches(presentation, cast):
    presentation.watch(
        f"subject[{cast}].ownedAttribute", presentation.update_shapes
    ).watch(
        f"subject[{cast}].ownedAttribute.association", presentation.update_shapes
    ).watch(f"subject[{cast}].ownedAttribute.name").watch(
        f"subject[{cast}].ownedAttribute.isStatic", presentation.update_shapes
    ).watch(f"subject[{cast}].ownedAttribute.isDerived").watch(
        f"subject[{cast}].ownedAttribute.visibility"
    ).watch(f"subject[{cast}].ownedAttribute.lowerValue").watch(
        f"subject[{cast}].ownedAttribute.upperValue"
    ).watch(f"subject[{cast}].ownedAttribute.defaultValue").watch(
        f"subject[{cast}].ownedAttribute.type"
    ).watch(f"subject[{cast}].ownedAttribute.type.name").watch(
        f"subject[{cast}].ownedAttribute.typeValue"
    )


def operation_watches(presentation, cast):
    presentation.watch(
        f"subject[{cast}].ownedOperation", presentation.update_shapes
    ).watch(f"subject[{cast}].ownedOperation.name").watch(
        f"subject[{cast}].ownedOperation.isAbstract", presentation.update_shapes
    ).watch(
        f"subject[{cast}].ownedOperation.isStatic", presentation.update_shapes
    ).watch(f"subject[{cast}].ownedOperation.visibility").watch(
        f"subject[{cast}].ownedOperation.ownedParameter.lowerValue"
    ).watch(f"subject[{cast}].ownedOperation.ownedParameter.upperValue").watch(
        f"subject[{cast}].ownedOperation.ownedParameter.type.name"
    ).watch(f"subject[{cast}].ownedOperation.ownedParameter.typeValue").watch(
        f"subject[{cast}].ownedOperation.ownedParameter.defaultValue"
    )


def attributes_compartment(subject):
    # We need to scope the attribute value, since the for loop changes it.
    def lazy_format(attribute):
        return lambda: format(attribute)

    return CssNode(
        "compartment",
        subject,
        Box(
            *(
                CssNode(
                    "attribute",
                    attribute,
                    Text(
                        text=lazy_format(attribute),
                    ),
                )
                for attribute in subject.ownedAttribute
                if not attribute.association
            ),
            draw=draw_top_separator,
        ),
    )


def operations_compartment(subject):
    def lazy_format(operation):
        return lambda: format(
            operation, visibility=True, type=True, multiplicity=True, default=True
        )

    return CssNode(
        "compartment",
        subject,
        Box(
            *(
                CssNode(
                    "operation",
                    operation,
                    Text(
                        text=lazy_format(operation),
                    ),
                )
                for operation in subject.ownedOperation
            ),
            draw=draw_top_separator,
        ),
    )
