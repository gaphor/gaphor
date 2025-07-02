import math

from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import (
    Classified,
    ElementPresentation,
)
from gaphor.diagram.shapes import (
    Box,
    CssNode,
    Text,
    draw_top_separator,
)
from gaphor.diagram.support import represents
from gaphor.SysML.sysml import ConstraintBlock
from gaphor.UML.classes.klass import (
    attribute_watches,
    attributes_compartment,
    operation_watches,
    operations_compartment,
)
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches
from gaphor.UML.compartments import name_compartment
from gaphor.UML.recipes import get_applied_stereotypes


def draw_rounded_rect(box, context, bounding_box):
    """Draw a rectangle with rounded corners."""
    cr = context.cairo
    rx = 4
    ry = 4
    width = bounding_box.width
    height = bounding_box.height

    cr.move_to(width, height - ry)
    cr.arc(width - rx, height - ry, rx, 0, 0.5 * math.pi)
    cr.line_to(rx, height)
    cr.arc(rx, height - ry, rx, 0.5 * math.pi, math.pi)
    cr.line_to(0, ry)
    cr.arc(rx, ry, rx, math.pi, 1.5 * math.pi)
    cr.line_to(width - rx, 0)
    cr.arc(width - rx, ry, rx, 1.5 * math.pi, 2 * math.pi)
    cr.close_path()
    cr.stroke()


@represents(ConstraintBlock)
class ConstraintBlockItem(Classified, ElementPresentation[ConstraintBlock]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id)

        self.watch("show_stereotypes", self.update_shapes).watch(
            "show_attributes", self.update_shapes
        ).watch("show_operations", self.update_shapes).watch(
            "subject[UML:NamedElement].name"
        ).watch("subject[UML:NamedElement].namespace.name").watch(
            "subject[Classifier].isAbstract", self.update_shapes
        )
        attribute_watches(self, "ConstraintBlock")
        operation_watches(self, "ConstraintBlock")
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    show_attributes: attribute[int] = attribute("show_attributes", int, default=False)

    show_operations: attribute[int] = attribute("show_operations", int, default=False)

    def additional_stereotypes(self):
        # Check if any other stereotypes are applied to avoid showing "constraintblock" redundantly
        if self.subject and not any(get_applied_stereotypes(self.subject)):
            return [self.diagram.gettext("constraintblock")]
        return ()

    def parameters_compartment(self):
        # Filter properties to only show those that are constraint parameters
        # (i.e., not typed by ConstraintBlock)
        if not self.subject:
            return Box()

        def lazy_format(attribute):
            return (
                lambda: f"{attribute.name}: {attribute.type.name}"
                if attribute.type
                else attribute.name
            )

        return CssNode(
            "compartment",
            self.subject,
            Box(
                CssNode(
                    "heading",
                    self.subject,
                    Text(text=self.diagram.gettext("parameters")),
                ),
                *(
                    CssNode("parameter", attribute, Text(text=lazy_format(attribute)))
                    for attribute in self.subject.ownedAttribute
                    if not (
                        attribute.type and isinstance(attribute.type, ConstraintBlock)
                    )
                ),
                draw=draw_top_separator,
            ),
        )

    def constraints_compartment(self):
        if not self.subject:
            return Box()
        return CssNode(
            "compartment",
            self.subject,
            Box(
                CssNode(
                    "heading",
                    self.subject,
                    Text(text=self.diagram.gettext("constraints")),
                ),
                CssNode("constraint", None, Text(text=lambda: "«expression»")),
                draw=draw_top_separator,
            ),
        )

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
            self.parameters_compartment(),
            self.constraints_compartment(),
            draw=draw_rounded_rect,
        )
