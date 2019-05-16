"""
Control flow and object flow implementation.

Contains also implementation to split flows using activity edge connectors.
"""

from math import atan, pi, sin, cos

from gaphor import UML
from gaphor.diagram.diagramline import NamedLine
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_RIGHT, ALIGN_TOP


node_classes = {
    UML.ForkNode: UML.JoinNode,
    UML.DecisionNode: UML.MergeNode,
    UML.JoinNode: UML.ForkNode,
    UML.MergeNode: UML.DecisionNode,
}


class FlowItem(NamedLine):
    """
    Representation of control flow and object flow. Flow item has name and
    guard. It can be splitted into two flows with activity edge connectors.
    """

    __uml__ = UML.ControlFlow

    __style__ = {"name-align": (ALIGN_RIGHT, ALIGN_TOP), "name-padding": (5, 15, 5, 5)}

    def __init__(self, id=None):
        super().__init__(id)
        self._guard = self.add_text("guard.value", editable=True)
        self.watch("subject<ControlFlow>.guard", self.on_control_flow_guard)
        self.watch("subject<ObjectFlow>.guard", self.on_control_flow_guard)

    def postload(self):
        try:
            self._guard.text = self.subject.guard.value
        except AttributeError as e:
            self._guard.text = ""
        super().postload()

    def on_control_flow_guard(self, event):
        subject = self.subject
        try:
            self._guard.text = subject.guard if subject else ""
        except AttributeError as e:
            self._guard.text = ""
        self.request_update()

    def draw_tail(self, context):
        cr = context.cairo
        cr.line_to(0, 0)
        cr.stroke()
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)
