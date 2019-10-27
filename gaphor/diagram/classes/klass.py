from gaphor import UML
from gaphor.diagram.classes.stereotype import stereotype_compartments
from gaphor.diagram.presentation import (
    ElementPresentation,
    Classified,
    from_package_str,
)
from gaphor.diagram.shapes import (
    Box,
    EditableText,
    Text,
    draw_border,
    draw_top_separator,
)
from gaphor.diagram.text import (
    TextAlign,
    VerticalAlign,
    FontStyle,
    FontWeight,
    TextDecoration,
)
from gaphor.diagram.support import represents


@represents(UML.Class)
@represents(UML.Stereotype)
class ClassItem(ElementPresentation, Classified):
    """This item visualizes a Class instance.

    A ClassItem contains two compartments: one for attributes and one for
    operations.
    """

    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.watch("show_stereotypes", self.update_shapes).watch(
            "show_attributes", self.update_shapes
        ).watch("show_operations", self.update_shapes).watch(
            "subject[NamedElement].name"
        ).watch(
            "subject[NamedElement].namespace.name"
        ).watch(
            "subject.appliedStereotype", self.update_shapes
        ).watch(
            "subject.appliedStereotype.classifier.name"
        ).watch(
            "subject.appliedStereotype.slot", self.update_shapes
        ).watch(
            "subject.appliedStereotype.slot.definingFeature.name"
        ).watch(
            "subject.appliedStereotype.slot.value", self.update_shapes
        ).watch(
            "subject[Classifier].isAbstract", self.update_shapes
        )
        attribute_watches(self, "Class")
        operation_watches(self, "Class")

    show_stereotypes = UML.properties.attribute("show_stereotypes", int)

    show_attributes = UML.properties.attribute("show_attributes", int, default=True)

    show_operations = UML.properties.attribute("show_operations", int, default=True)

    def update_shapes(self, event=None):
        def additional_stereotypes():
            if isinstance(self.subject, UML.Stereotype):
                return ["stereotype"]
            elif UML.model.is_metaclass(self.subject):
                return ["metaclass"]
            else:
                return ()

        self.shape = Box(
            Box(
                Text(
                    text=lambda: UML.model.stereotypes_str(
                        self.subject, additional_stereotypes()
                    ),
                    style={"min-width": 0, "min-height": 0},
                ),
                EditableText(
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
                    style={"font": "sans 8", "min-width": 0, "min-height": 0},
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
                "min-width": 100,
                "min-height": 50,
                "vertical-align": VerticalAlign.TOP,
            },
            draw=draw_border,
        )

    # TODO: Needs implementing, see also gaphor/diagram/editors.py
    def item_at(self, x, y):
        if 0 > x > self.width:
            return None

        if y < self.shape.sizes[0][1]:
            print("in header")
        elif y < self.shape.sizes[1][1]:
            print("in attr comp")

        return self


def attribute_watches(presentation, cast):
    presentation.watch(
        f"subject[{cast}].ownedAttribute", presentation.update_shapes
    ).watch(
        f"subject[{cast}].ownedAttribute.association", presentation.update_shapes
    ).watch(
        f"subject[{cast}].ownedAttribute.name"
    ).watch(
        f"subject[{cast}].ownedAttribute.isStatic", presentation.update_shapes
    ).watch(
        f"subject[{cast}].ownedAttribute.isDerived"
    ).watch(
        f"subject[{cast}].ownedAttribute.visibility"
    ).watch(
        f"subject[{cast}].ownedAttribute.lowerValue"
    ).watch(
        f"subject[{cast}].ownedAttribute.upperValue"
    ).watch(
        f"subject[{cast}].ownedAttribute.defaultValue"
    ).watch(
        f"subject[{cast}].ownedAttribute.typeValue"
    )


def operation_watches(presentation, cast):
    presentation.watch(
        f"subject[{cast}].ownedOperation", presentation.update_shapes
    ).watch(f"subject[{cast}].ownedOperation.name").watch(
        f"subject[{cast}].ownedOperation.isAbstract", presentation.update_shapes
    ).watch(
        f"subject[{cast}].ownedOperation.isStatic", presentation.update_shapes
    ).watch(
        f"subject[{cast}].ownedOperation.visibility"
    ).watch(
        f"subject[{cast}].ownedOperation.returnResult.lowerValue"
    ).watch(
        f"subject[{cast}].ownedOperation.returnResult.upperValue"
    ).watch(
        f"subject[{cast}].ownedOperation.returnResult.typeValue"
    ).watch(
        f"subject[{cast}].ownedOperation.formalParameter.lowerValue"
    ).watch(
        f"subject[{cast}].ownedOperation.formalParameter.upperValue"
    ).watch(
        f"subject[{cast}].ownedOperation.formalParameter.typeValue"
    ).watch(
        f"subject[{cast}].ownedOperation.formalParameter.defaultValue"
    )


def attributes_compartment(subject):
    # We need to fix the attribute value, since the for loop changes it.
    def lazy_format(attribute):
        # str(), so we never ever get an error on a property part of an association
        return lambda: (UML.format(attribute))

    return Box(
        *(
            Text(
                text=lazy_format(attribute),
                style={
                    "text-align": TextAlign.LEFT,
                    "text-decoration": TextDecoration.UNDERLINE
                    if attribute.isStatic
                    else TextDecoration.NONE,
                },
            )
            for attribute in subject.ownedAttribute
            if not attribute.association
        ),
        style={"padding": (4, 4, 4, 4), "min-height": 8},
        draw=draw_top_separator,
    )


def operations_compartment(subject):
    def lazy_format(operation):
        return lambda: UML.format(
            operation, visibility=True, type=True, multiplicity=True, default=True
        )

    return Box(
        *(
            Text(
                text=lazy_format(operation),
                style={
                    "text-align": TextAlign.LEFT,
                    "font-style": FontStyle.ITALIC
                    if operation.isAbstract
                    else FontStyle.NORMAL,
                    "text-decoration": TextDecoration.UNDERLINE
                    if operation.isStatic
                    else TextDecoration.NONE,
                },
            )
            for operation in subject.ownedOperation
        ),
        style={"padding": (4, 4, 4, 4), "min-height": 8},
        draw=draw_top_separator,
    )
