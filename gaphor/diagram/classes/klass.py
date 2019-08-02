from gaphor import UML
from gaphor.diagram.classes.stereotype import stereotype_compartments
from gaphor.diagram.presentation import ElementPresentation, Classified
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

	A ClassItem contains two compartments: one for
	attributes and one for operations.
    """

    __style__ = {
        "extra-space": "compartment",
        "abstract-feature-font": "sans italic 10",
    }

    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.watch("show_stereotypes_attrs", self.update_shapes).watch(
            "show_attributes", self.update_shapes
        ).watch("show_operations", self.update_shapes).watch(
            "subject", self.update_shapes
        ).watch(
            "subject<NamedElement>.name"
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
            "subject<Classifier>.isAbstract", self.update_shapes
        ).watch(
            "subject<Class>.ownedAttribute", self.update_shapes
        ).watch(
            "subject<Class>.ownedOperation", self.update_shapes
        ).watch(
            "subject<Class>.ownedAttribute.association", self.update_shapes
        ).watch(
            "subject<Class>.ownedAttribute.name"
        ).watch(
            "subject<Class>.ownedAttribute.isStatic", self.update_shapes
        ).watch(
            "subject<Class>.ownedAttribute.isDerived"
        ).watch(
            "subject<Class>.ownedAttribute.visibility"
        ).watch(
            "subject<Class>.ownedAttribute.lowerValue"
        ).watch(
            "subject<Class>.ownedAttribute.upperValue"
        ).watch(
            "subject<Class>.ownedAttribute.defaultValue"
        ).watch(
            "subject<Class>.ownedAttribute.typeValue"
        ).watch(
            "subject<Class>.ownedOperation.name"
        ).watch(
            "subject<Class>.ownedOperation.isAbstract", self.update_shapes
        ).watch(
            "subject<Class>.ownedOperation.isStatic", self.update_shapes
        ).watch(
            "subject<Class>.ownedOperation.visibility"
        ).watch(
            "subject<Class>.ownedOperation.returnResult.lowerValue"
        ).watch(
            "subject<Class>.ownedOperation.returnResult.upperValue"
        ).watch(
            "subject<Class>.ownedOperation.returnResult.typeValue"
        ).watch(
            "subject<Class>.ownedOperation.formalParameter.lowerValue"
        ).watch(
            "subject<Class>.ownedOperation.formalParameter.upperValue"
        ).watch(
            "subject<Class>.ownedOperation.formalParameter.typeValue"
        ).watch(
            "subject<Class>.ownedOperation.formalParameter.defaultValue"
        )

    show_stereotypes_attrs = UML.properties.attribute("show_stereotypes_attrs", int)

    show_attributes = UML.properties.attribute("show_attributes", int, default=1)

    show_operations = UML.properties.attribute("show_operations", int, default=1)

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
            *(
                self.show_stereotypes_attrs
                and stereotype_compartments(self.subject)
                or []
            ),
            style={
                "min-width": 100,
                "min-height": 50,
                "vertical-align": VerticalAlign.TOP,
            },
            draw=draw_border,
        )

    def load(self, name, value):
        if name in ("show-attributes", "show-operations"):
            super().load(name.replace("-", "_"), value)
        else:
            super().load(name, value)

    # TODO: Needs implementing, see also gaphor/diagram/editors.py
    def item_at(self, x, y):
        if 0 > x > self.width:
            return None

        if y < self.shape.sizes[0][1]:
            print("in header")
        elif y < self.shape.sizes[1][1]:
            print("in attr comp")

        return self


def attributes_compartment(subject):
    # We need to fix the attribute value, since the for loop changes it.
    def lazy_format(attribute):
        # str(), so we never ever get an error on a property part of an association
        return lambda: (UML.format(attribute))

    return Box(
        *(
            Text(text=lazy_format(attribute), style={"text-align": TextAlign.LEFT})
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
                    "font": "sans italic 10" if operation.isAbstract else "sans 10",
                },
            )
            for operation in subject.ownedOperation
        ),
        style={"padding": (4, 4, 4, 4), "min-height": 8},
        draw=draw_top_separator,
    )
