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
from gaphor.core.styling import JustifyContent
from gaphor.diagram.presentation import Classified, ElementPresentation, text_name
from gaphor.diagram.shapes import Box, stroke
from gaphor.diagram.support import represents
from gaphor.UML.classes.stereotype import stereotype_compartments, stereotype_watches
from gaphor.UML.shapes import text_stereotypes


@represents(UML.Node)
@represents(UML.Device)
class NodeItem(Classified, ElementPresentation):
    """Representation of node or device from UML Deployment package."""

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id)

        self.watch("children", self.update_shapes)
        self.watch("show_stereotypes", self.update_shapes)
        self.watch("subject[NamedElement].name")
        self.watch("subject[Node].ownedConnector", self.update_shapes)
        stereotype_watches(self)

    show_stereotypes: attribute[int] = attribute("show_stereotypes", int)

    def update_shapes(self, event=None):
        self.shape = Box(
            Box(
                text_stereotypes(
                    self,
                    lambda: [self.diagram.gettext("device")]
                    if isinstance(self.subject, UML.Device)
                    else [],
                ),
                text_name(self),
                style={
                    "padding": (4, 4, 4, 4),
                    "justify-content": JustifyContent.START,
                },
            ),
            *(self.show_stereotypes and stereotype_compartments(self.subject) or []),
            style={
                "justify-content": JustifyContent.START
                if self.diagram and self.children
                else JustifyContent.CENTER,
            },
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
