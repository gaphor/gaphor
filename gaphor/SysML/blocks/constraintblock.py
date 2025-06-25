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


@represents(ConstraintBlock)
class ConstraintBlockItem(Classified, ElementPresentation[ConstraintBlock]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("show_stereotypes", self.update_shapes).watch(
            "show_attributes", self.update_shapes
        ).watch("show_operations", self.update_shapes).watch(
            "subject[UML:NamedElement].name"
        ).watch("subject[UML:NamedElement].namespace.name"
        ).watch("subject[Classifier].isAbstract", self.update_shapes)
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