"""Actor item classes."""

from math import pi

from gaphas.constraint import constraint
from gaphas.geometry import distance_line_point
from gaphas.item import SE, SW
from gaphas.port import LinePort
from gaphas.position import Position
from gaphas.solver import REQUIRED, STRONG, variable

from gaphor import UML
from gaphor.diagram.presentation import Classified, ElementPresentation, text_name
from gaphor.diagram.shapes import Box, IconBox, stroke
from gaphor.diagram.support import represents
from gaphor.UML.compartments import text_stereotypes

HEAD = 11
ARM = 19
NECK = 10
BODY = 20


@represents(UML.Actor)
class ActorItem(Classified, ElementPresentation):
    """Actor item is a classifier in icon mode.

    Maybe it should be possible to switch to compartment mode in the
    future.
    """

    text_height = variable(strength=REQUIRED, varname="_text_height")

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=ARM * 2, height=HEAD + NECK + BODY + ARM)

        # Allow to connect to the bottom of the actor, below the actor name
        self._sub_text_port = LinePort(
            Position(0, 0, strength=STRONG), Position(0, 0, strength=STRONG)
        )
        self._ports.append(self._sub_text_port)

        self.text_height = 20.0

        add = diagram.connections.add_constraint
        add(
            self,
            constraint(
                horizontal=(self._handles[SW].pos, self._sub_text_port.start),
                delta=self.text_height,
            ),
        )
        add(
            self,
            constraint(vertical=(self._handles[SW].pos, self._sub_text_port.start)),
        )
        add(
            self,
            constraint(
                horizontal=(self._handles[SE].pos, self._sub_text_port.end),
                delta=self.text_height,
            ),
        )
        add(self, constraint(vertical=(self._handles[SE].pos, self._sub_text_port.end)))

        self.watch("subject.name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject[Classifier].isAbstract", self.update_shapes)

    def update_shapes(self, event=None):
        self.shape = IconBox(
            Box(
                draw=draw_actor,
            ),
            text_stereotypes(self),
            text_name(self),
        )

    def update(self, context):
        super().update(context)
        _xs, ys = list(zip(*self.shape.sizes))
        self.text_height = sum(ys)

    def point(self, x: float, y: float) -> float:
        return min(  # type: ignore[no-any-return]
            super().point(x, y),
            distance_line_point(
                self._sub_text_port.start, self._sub_text_port.end, (x, y)
            )[0],
        )

    def postload(self):
        super().postload()
        self.diagram.connections.solve()


def draw_actor(box, context, bounding_box):
    """Draw actor's icon creature."""
    cr = context.cairo

    fx = bounding_box.width / (ARM * 2)
    fy = bounding_box.height / (HEAD + NECK + BODY + ARM)

    x = ARM * fx
    y = (HEAD / 2) * fy
    cy = HEAD * fy

    cr.move_to(x + HEAD * fy / 2.0, y)
    cr.arc(x, y, HEAD * fy / 2.0, 0, 2 * pi)

    cr.move_to(x, y + cy / 2)
    cr.line_to(ARM * fx, (HEAD + NECK + BODY) * fy)

    cr.move_to(0, (HEAD + NECK) * fy)
    cr.line_to(ARM * 2 * fx, (HEAD + NECK) * fy)

    cr.move_to(0, (HEAD + NECK + BODY + ARM) * fy)
    cr.line_to(ARM * fx, (HEAD + NECK + BODY) * fy)
    cr.line_to(ARM * 2 * fx, (HEAD + NECK + BODY + ARM) * fy)
    stroke(context, fill=False)
