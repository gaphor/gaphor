from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
)
from gaphor.diagram.shapes import (
    Box,
    CssNode,
    Text,
    draw_border,
    draw_top_separator,
)
from gaphor.diagram.support import represents
from gaphor.SysML.sysml import InterfaceBlock, ValueType
from gaphor.UML.classes.klass import attributes_compartment, operation_watches
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches
from gaphor.UML.compartments import name_compartment
from gaphor.UML.umlfmt import format_operation, format_property


@represents(InterfaceBlock)
class InterfaceBlockItem(Classified, ElementPresentation[InterfaceBlock]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("show_stereotypes", self.update_shapes).watch(
            "show_parts", self.update_shapes
        ).watch("show_references", self.update_shapes).watch(
            "show_values", self.update_shapes
        ).watch("show_operations", self.update_shapes).watch("subject.name").watch(
            "subject.name"
        ).watch("subject.namespace.name").watch(
            "subject[Classifier].isAbstract", self.update_shapes
        ).watch("subject[Class].ownedAttribute.aggregation", self.update_shapes)
        operation_watches(self, "Block")
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    show_parts: attribute[int] = attribute("show_parts", int, default=False)

    show_references: attribute[int] = attribute("show_references", int, default=False)

    show_values: attribute[int] = attribute("show_values", int, default=False)

    show_attributes: attribute[int] = attribute("show_attributes", int, default=False)

    show_operations: attribute[int] = attribute("show_operations", int, default=False)

    def additional_stereotypes(self):
        from gaphor.RAAML import raaml

        if isinstance(self.subject, raaml.Situation):
            return [self.diagram.gettext("Situation")]
        elif isinstance(self.subject, raaml.ControlStructure):
            return [self.diagram.gettext("ControlStructure")]
        elif isinstance(self.subject, InterfaceBlock):
            return [self.diagram.gettext("interfaceblock")]
        return ()

    def update_shapes(self, event=None):
        self.shape = Box(
            name_compartment(self, self.additional_stereotypes),
            *(
                self.show_references
                and self.subject
                and [
                    self.block_compartment(
                        self.diagram.gettext("references"),
                        lambda a: not a.association and a.aggregation != "composite",
                        "reference",
                    )
                ]
                or []
            ),
            *(
                self.show_values
                and self.subject
                and [
                    self.block_compartment(
                        self.diagram.gettext("values"),
                        lambda a: isinstance(a.type, ValueType)
                        and a.aggregation == "composite",
                        "value",
                    )
                ]
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
                and [
                    self.operations_compartment(
                        self.diagram.gettext("operations"), self.subject
                    ),
                ]
                or []
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            draw=draw_border,
        )

    def block_compartment(self, name, predicate, css_name):
        # We need to fix the attribute value, since the for loop changes it.
        def lazy_format(attribute):
            return lambda: format_property(attribute) or self.diagram.gettext("unnamed")

        return CssNode(
            "compartment",
            self.subject,
            Box(
                CssNode(
                    "heading",
                    self.subject,
                    Text(text=name),
                ),
                *(
                    CssNode(css_name, attribute, Text(text=lazy_format(attribute)))
                    for attribute in self.subject.ownedAttribute
                    if predicate(attribute)
                ),
                draw=draw_top_separator,
            ),
        )

    def operations_compartment(self, name, predicate):
        def lazy_format(operation):
            return lambda: format_operation(operation) or self.diagram.gettext(
                "unnamed"
            )

        return CssNode(
            "compartment",
            self.subject,
            Box(
                CssNode(
                    "heading",
                    self.subject,
                    Text(text=name),
                ),
                *(
                    CssNode("operation", operation, Text(text=lazy_format(operation)))
                    for operation in self.subject.ownedOperation
                ),
                draw=draw_top_separator,
            ),
        )
