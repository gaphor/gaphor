"""
Control flow and object flow implementation.

Contains also implementation to split flows using activity edge connectors.
"""

from math import atan, atan2, pi, sin, cos

from gaphor import UML
from gaphor.UML.presentation import LinePresentation
from gaphor.diagram.diagramline import NamedLine
from gaphor.diagram.text import Name, Guard, TextAlign, VerticalAlign, middle_segment
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_RIGHT, ALIGN_TOP
from gaphor.diagram.support import represents
from gaphor.diagram.shapes import Line, draw_arrow_tail


@represents(UML.ControlFlow)
class FlowItem(LinePresentation):
    """
    Representation of control flow and object flow. Flow item has name and
    guard. It can be splitted into two flows with activity edge connectors.
    """

    def __init__(self, id=None, model=None):
        super().__init__(id, model)

        self._name = Name(
            self,
            style={"text-align": TextAlign.RIGHT, "vertical-align": VerticalAlign.TOP},
        )
        self._guard = Guard(self)
        self.layout = Line(self._name, draw_tail=draw_arrow_tail)

    # TODO: draw name and guard (and possibly stereotype)

    def draw(self, context):
        self.layout.draw(context.cairo, [h.pos for h in self.handles()])
