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

Stick with BehaviorExecutionSpecification, since it has a [0..1] relation to behavior, whereas
ActionExecutionSpecification has a [1] relation to action.
"""
from gaphas import Handle, Item
from gaphas.connector import LinePort
from gaphas.geometry import Rectangle, distance_rectangle_point

from gaphor import UML
from gaphor.diagram.shapes import Box, draw_border
from gaphor.diagram.support import represents
from gaphor.UML.modelfactory import stereotypes_str


@represents(UML.ExecutionSpecification)
class ExecutionSpecificationItem(UML.Presentation[UML.ExecutionSpecification], Item):
    """
    Representation of interaction execution specification.
    """

    def __init__(self, id=None, model=None):
        super().__init__(id, model)
        self._min_height = 10

        ht, hb = Handle(), Handle()
        ht.connectable = True

        # TODO: need better interface for this!
        self._handles.append(ht)
        self._handles.append(hb)
        # self._ports.append(LinePort(h1.pos, h2.pos))

        self.constraint(above=(ht.pos, hb.pos), delta=self._min_height)
        self.constraint(vertical=(ht.pos, hb.pos))

        self.shape = Box(
            style={"fill": "white"}, draw=draw_border
        )  # self.draw_execution_specification)

    def dimensions(self):
        d = 10
        pt, pb = (h.pos for h in self._handles)
        return Rectangle(pt.x - d / 2, pt.y, d, pb.y - pt.y)

    def draw(self, context):
        self.shape.draw(context, self.dimensions())

    def point(self, pos):
        return distance_rectangle_point(self.dimensions(), pos)

    def save(self, save_func):
        super().save(save_func)

    def load(self, name, value):
        super().load(name, value)
