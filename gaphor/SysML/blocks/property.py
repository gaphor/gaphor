"""Property item."""

from gaphor import UML
from gaphor.core.modeling.diagram import Diagram
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.drop import drop
from gaphor.diagram.presentation import ElementPresentation, Named
from gaphor.diagram.shapes import Box, CssNode, Text, draw_border
from gaphor.diagram.support import represents
from gaphor.SysML.sysml import Constraint
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches
from gaphor.UML.compartments import text_stereotypes
from gaphor.UML.drop import drop_element
from gaphor.UML.umlfmt import format_property

# Sibling module imports
from .constraintparameter import ConstraintParameterItem
from .constraintproperty import ConstraintPropertyItem


@represents(UML.Property)
class PropertyItem(Named, ElementPresentation[UML.Property]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("show_stereotypes", self.update_shapes)
        self.watch("subject[Property].name")
        self.watch("subject[Property].type.name")
        self.watch("subject[Property].typeValue")
        self.watch("subject[Property].lowerValue")
        self.watch("subject[Property].upperValue")
        self.watch("subject[Property].aggregation", self.update_shapes)
        stereotype_watches(self)
        self.watch("subject[Property].type", self.update_shapes)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    def update_shapes(self, event=None):
        """
        Update the shapes for a standard Property.

        Constraint Properties are now handled by ConstraintPropertyItem,
        so this item no longer needs special rendering for them.
        """
        self.shape = Box(
            CssNode(
                "compartment",
                self.subject,
                Box(
                    text_stereotypes(self),
                    CssNode(
                        "name",
                        self.subject,
                        Text(
                            text=lambda: format_property(
                                self.subject, type=True, multiplicity=True
                            )
                            or "",
                        ),
                    ),
                ),
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            draw=draw_border,
        )


@drop.register(UML.Property, Diagram)
def drop_property(element: UML.Property, diagram: Diagram, x: int, y: int):
    """Drop a property.

    - If the property is a constraint parameter (owned by a constraint),
      create a ConstraintParameterItem.
    - If the property is typed by a Constraint, create a
      ConstraintPropertyItem.
    - Otherwise, fall back to the default drop behavior.
    """
    if isinstance(element.owner, Constraint):
        item_class = ConstraintParameterItem
    elif isinstance(element.type, Constraint):
        item_class = ConstraintPropertyItem
    else:
        return drop_element(element, diagram, x, y)

    item = diagram.create(item_class)
    item.matrix.translate(x, y)
    item.subject = element
    return item
