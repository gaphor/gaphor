"""
Node item may represent a node or a device UML metamodel classes.

Grouping
========
Node item can group following items

- other nodes, which are represented with Node.nestedNode on UML metamodel
  level
- deployed artifacts using deployment
- components, which are parts of a node acting as structured classifier
  (nodes may have internal structures)

Node item grouping logic is implemented in `gaphor.adapters.grouping`
module.
"""

from gaphor import UML
from gaphor.core.modeling.properties import attribute
from gaphor.diagram.presentation import Classified, ElementPresentation
from gaphor.diagram.shapes import Box, EditableText, Text, VerticalAlign
from gaphor.diagram.support import represents
from gaphor.diagram.text import FontWeight
from gaphor.UML.classes.stereotype import stereotype_compartments


@represents(UML.Node)
@represents(UML.Device)
class NodeItem(ElementPresentation, Classified):
    """
    Representation of node or device from UML Deployment package.
    """

    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self.watch("show_stereotypes", self.update_shapes)
        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype", self.update_shapes)
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject.appliedStereotype.slot", self.update_shapes)
        self.watch("subject.appliedStereotype.slot.definingFeature.name")
        self.watch("subject.appliedStereotype.slot.value", self.update_shapes)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                Text(
                    text=lambda: UML.model.stereotypes_str(
                        self.subject,
                        isinstance(self.subject, UML.Device) and ("device",) or (),
                    ),
                    style={"min-width": 0, "min-height": 0},
                ),
                EditableText(
                    text=lambda: self.subject.name or "",
                    style={"font-weight": FontWeight.BOLD},
                ),
                style={"padding": (4, 4, 4, 4)},
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            style={
                "min-width": 100,
                "min-height": 50,
                "vertical-align": VerticalAlign.TOP
                if self.canvas and self.canvas.get_children(self)
                else VerticalAlign.MIDDLE,
            },
            draw=draw_node
        )


def draw_node(box, context, bounding_box):
    cr = context.cairo

    d = 10
    w = bounding_box.width
    h = bounding_box.height

    cr.rectangle(0, 0, w, h)

    cr.move_to(0, 0)
    cr.line_to(d, -d)
    cr.line_to(w + d, -d)
    cr.line_to(w + d, h - d)
    cr.line_to(w, h)
    cr.move_to(w, 0)
    cr.line_to(w + d, -d)

    cr.stroke()
