"""An ExecutionSpecification is defined by a white recrange overlaying the
lifeline.

  ,----------.
  | lifeline |
  `----------'
       | --- Lifeline
      ,+. -- ExecutionOccurrenceSpecification
      | | -- ExecutionSpecification
      `+' -- ExecutionOccurrentSpecification
       |

    ExecutionOccurrenceSpecification.covered <--> Lifeline.coveredBy
    ExecutionOccurrenceSpecification.execution <--> ExecutionSpecification.execution

TODO:ExecutionSpecification is abstract. Should use either
ActionExecutionSpecification or BehaviorExecutionSpecification.
What's the difference?

Stick with BehaviorExecutionSpecification, since it has a [0..1] relation to
behavior, whereas ActionExecutionSpecification has a [1] relation to action.
"""
import ast

from gaphas import Handle
from gaphas.connector import LinePort, Position
from gaphas.constraint import constraint
from gaphas.geometry import Rectangle, distance_rectangle_point
from gaphas.solver import WEAK

from gaphor import UML
from gaphor.core.modeling import Presentation
from gaphor.diagram.presentation import HandlePositionUpdate, postload_connect
from gaphor.diagram.shapes import Box, draw_border
from gaphor.diagram.support import represents


@represents(UML.ExecutionSpecification)
@represents(UML.BehaviorExecutionSpecification)
class ExecutionSpecificationItem(
    Presentation[UML.ExecutionSpecification], HandlePositionUpdate
):
    """Representation of interaction execution specification."""

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id)
        self._connections = diagram.connections

        self.bar_width = 12

        ht, hb = Handle(), Handle()
        ht.connectable = True

        self._handles = [ht, hb]
        self.watch_handle(ht)
        self.watch_handle(hb)

        self._connections.add_constraint(self, constraint(vertical=(ht.pos, hb.pos)))

        r = self.bar_width / 2
        nw = Position(-r, 0, strength=WEAK)
        ne = Position(r, 0, strength=WEAK)
        se = Position(r, 0, strength=WEAK)
        sw = Position(-r, 0, strength=WEAK)

        for c in (
            constraint(horizontal=(nw, ht.pos)),
            constraint(horizontal=(ne, ht.pos)),
            constraint(horizontal=(sw, hb.pos)),
            constraint(horizontal=(se, hb.pos)),
            constraint(vertical=(nw, ht.pos), delta=-r),
            constraint(vertical=(ne, ht.pos), delta=r),
            constraint(vertical=(sw, hb.pos), delta=-r),
            constraint(vertical=(se, hb.pos), delta=r),
        ):
            self._connections.add_constraint(self, c)

        self._ports = [LinePort(nw, sw), LinePort(ne, se)]

        self.shape = Box(
            style={"background-color": (1.0, 1.0, 1.0, 1.0)}, draw=draw_border
        )

    def handles(self):
        return self._handles

    def ports(self):
        return self._ports

    @property
    def top(self):
        return self._handles[0]

    @property
    def bottom(self):
        return self._handles[1]

    def dimensions(self):
        d = self.bar_width
        pt, pb = (h.pos for h in self._handles)
        return Rectangle(pt.x - d / 2, pt.y, d, y1=pb.y)

    def pre_update(self, context):
        pass

    def post_update(self, context):
        pass

    def draw(self, context):
        self.shape.draw(context, self.dimensions())

    def point(self, x, y):
        return distance_rectangle_point(self.dimensions(), (x, y))

    def save(self, save_func):
        def save_connection(name, handle):
            c = self._connections.get_connection(handle)
            if c:
                save_func(name, c.connected)

        points = [tuple(map(float, h.pos)) for h in self.handles()]

        save_func("matrix", tuple(self.matrix))
        save_func("points", points)
        save_connection("head-connection", self.handles()[0])
        super().save(save_func)

    def load(self, name, value):
        if name == "matrix":
            self.matrix.set(*ast.literal_eval(value))
        elif name == "points":
            points = ast.literal_eval(value)
            for h, p in zip(self.handles(), points):
                h.pos = p
        elif name == "head-connection":
            self._load_head_connection = value
        else:
            super().load(name, value)

    def postload(self):
        if hasattr(self, "_load_head_connection"):
            postload_connect(self, self.handles()[0], self._load_head_connection)
            del self._load_head_connection

        super().postload()
