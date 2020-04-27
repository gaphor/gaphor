"""
An ExecutionSpecification is defined by a white recrange overlaying the lifeline



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

from gaphas import Handle, Item
from gaphas.connector import LinePort, Position
from gaphas.geometry import Rectangle, distance_rectangle_point
from gaphas.solver import WEAK

from gaphor import UML
from gaphor.core.modeling import Presentation
from gaphor.diagram.presentation import postload_connect
from gaphor.diagram.shapes import Box, draw_border
from gaphor.diagram.support import represents
from gaphor.UML.modelfactory import stereotypes_str


@represents(UML.ExecutionSpecification)
class ExecutionSpecificationItem(Presentation[UML.ExecutionSpecification], Item):
    """
    Representation of interaction execution specification.
    """

    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        self.bar_width = 12

        ht, hb = Handle(), Handle()
        ht.connectable = True

        # TODO: need better interface for this!
        self._handles.append(ht)
        self._handles.append(hb)

        self.constraint(vertical=(ht.pos, hb.pos))

        r = self.bar_width / 2
        nw = Position((-r, 0), strength=WEAK)
        ne = Position((r, 0), strength=WEAK)
        se = Position((r, 0), strength=WEAK)
        sw = Position((-r, 0), strength=WEAK)

        self.constraint(horizontal=(sw, hb.pos))
        self.constraint(horizontal=(se, hb.pos))

        self._ports.append(LinePort(nw, sw))
        self._ports.append(LinePort(ne, se))

        self.shape = Box(style={"fill": "white"}, draw=draw_border)

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

    def draw(self, context):
        self.shape.draw(context, self.dimensions())

    def point(self, pos):
        return distance_rectangle_point(self.dimensions(), pos)

    def save(self, save_func):
        def save_connection(name, handle):
            assert self.canvas
            c = self.canvas.get_connection(handle)
            if c:
                save_func(name, c.connected)

        points = [tuple(map(float, h.pos)) for h in self.handles()]

        save_func("matrix", tuple(self.matrix))
        save_func("points", points)
        save_connection("head-connection", self.handles()[0])
        super().save(save_func)

    def load(self, name, value):
        if name == "matrix":
            self.matrix = ast.literal_eval(value)
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
