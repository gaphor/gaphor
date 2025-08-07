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

from .constraintparameter import ConstraintParameterItem
from .constraintproperty import ConstraintPropertyItem

SPACER_LINES = 1  # increase to 2 if you want a larger top gap


@represents(UML.Property)
class PropertyItem(Named, ElementPresentation[UML.Property]):
    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        # Diagram-only counter: when > 0 we render an extra spacer
        self._visual_children_count: int = 0

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

    def _recount_visual_children(self) -> int:
        count = 0
        try:
            for c in self.children or []:
                if isinstance(getattr(c, "subject", None), UML.Property):
                    count += 1
        except Exception:
            pass
        self._visual_children_count = count
        return count

    def _has_nested_properties(self) -> bool:
        # Prefer cached counter; fall back to recount to catch de-nesting
        return self._visual_children_count > 0 or self._recount_visual_children() > 0

    def _spacer_compartment(self):
        # Spacer with visible height: draw SPACER_LINES empty text lines to
        # create vertical room under the title.
        def spacer_text():
            return (" \n" * SPACER_LINES).rstrip("\n")

        return CssNode("compartment", self.subject, Box(Text(text=spacer_text)))

    def update_shapes(self, event=None):
        def name_text():
            return format_property(self.subject, type=True, multiplicity=True) or ""

        top_compartment = CssNode(
            "compartment",
            self.subject,
            Box(
                text_stereotypes(self),
                # Keep original font/style for the name
                CssNode("name", self.subject, Text(text=name_text)),
            ),
        )

        compartments = [top_compartment]
        if self._has_nested_properties():
            compartments.append(self._spacer_compartment())

        self.shape = Box(
            *compartments,
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            draw=draw_border,
        )

    def request_update(self):
        # Self-heal: recalc child state on interaction and rebuild shape if it
        # changed, so de-nesting always re-centers the title.
        try:
            prev = self._visual_children_count
            self._recount_visual_children()
            if (prev > 0) != (self._visual_children_count > 0):
                self.update_shapes()
        except Exception:
            pass
        return super().request_update()


@drop.register(UML.Property, Diagram)
def drop_property(element: UML.Property, diagram: Diagram, x: int, y: int):
    if isinstance(element.type, Constraint):
        item_class = ConstraintPropertyItem
    elif isinstance(element.owner, Constraint):
        item_class = ConstraintParameterItem
    else:
        return drop_element(element, diagram, x, y)

    item = diagram.create(item_class)
    item.matrix.translate(x, y)
    item.subject = element
    return item
