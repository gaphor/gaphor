"""
Control flow and object flow implementation.

Contains also implementation to split flows using activity edge connectors.
"""

from math import atan, atan2, pi, sin, cos

from gaphor import UML
from gaphor.UML.presentation import LinePresentation
from gaphor.diagram.diagramline import NamedLine
from gaphor.diagram.text import FloatingText, TextAlign, VerticalAlign, middle_segment
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

        self.name = FloatingText(
            text=lambda: self.subject and self.subject.name or "",
            style={"text-align": TextAlign.RIGHT, "vertical-align": VerticalAlign.TOP},
        )
        self.watch("subject<NamedElement>.name")

        self.guard = FloatingText(
            text=lambda: self.subject and self.subject.guard or ""
        )
        self.watch("subject<ControlFlow>.guard")
        self.watch("subject<ObjectFlow>.guard")

        self.layout = Line(self.name, self.guard, draw_tail=draw_arrow_tail)
