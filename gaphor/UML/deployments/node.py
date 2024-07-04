"""Node item may represent a node or a device UML metamodel classes.

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
from gaphor.diagram.shapes import Box, stroke
from gaphor.diagram.support import represents
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches
from gaphor.UML.compartments import name_compartment


@represents(UML.Node)
@represents(UML.Device)
class NodeItem(Classified, ElementPresentation):
    """Representation of node or device from UML Deployment package."""

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("children", self.update_shapes)
        self.watch("show_stereotypes", self.update_shapes)
        self.watch("subject.name")
        self.watch("subject[Node].ownedConnector", self.update_shapes)
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    def update_shapes(self, event=None):
        self.shape = Box(
            name_compartment(
                self,
                lambda: [self.diagram.gettext("device")]
                if isinstance(self.subject, UML.Device)
                else [],
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            draw=draw_node,
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

    stroke(context, fill=True)
