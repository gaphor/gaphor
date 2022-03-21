"""Activity control nodes."""

import ast
import math

from gaphas.constraint import constraint
from gaphas.geometry import Rectangle, distance_line_point
from gaphas.item import Handle, LinePort
from gaphas.matrix import Matrix
from gaphas.util import path_ellipse

from gaphor import UML
from gaphor.core.modeling import Presentation
from gaphor.core.modeling.properties import association, attribute, relation_one
from gaphor.diagram.presentation import ElementPresentation, HandlePositionUpdate, Named
from gaphor.diagram.shapes import Box, IconBox, Text, stroke
from gaphor.diagram.support import represents
from gaphor.i18n import gettext
from gaphor.UML.recipes import stereotypes_str

DEFAULT_JOIN_SPEC = "and"


def no_movable_handles(item):
    for h in item._handles:
        h.movable = False


class ActivityNodeItem(Named):
    """Basic class for simple activity nodes.

    Simple activity node is not resizable.
    """


@represents(UML.InitialNode)
class InitialNodeItem(ActivityNodeItem, ElementPresentation):
    """Representation of initial node.

    Initial node has name which is put near top-left side of node.
    """

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=20, height=20)
        no_movable_handles(self)

        self.shape = IconBox(
            Box(draw=draw_initial_node),
            # Text should be left-top
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(text=lambda: self.subject and self.subject.name or ""),
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")


def draw_initial_node(_box, context, _bounding_box):
    cr = context.cairo
    if stroke := context.style["color"]:
        cr.set_source_rgba(*stroke)

    r = 10
    d = r * 2
    path_ellipse(cr, r, r, d, d)
    cr.set_line_width(0.01)
    cr.fill()


@represents(UML.ActivityFinalNode)
class ActivityFinalNodeItem(ActivityNodeItem, ElementPresentation):
    """Representation of activity final node.

    Activity final node has name which is put near right-bottom side of
    node.
    """

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=30, height=30)
        no_movable_handles(self)

        self.shape = IconBox(
            Box(draw=draw_activity_final_node),
            # Text should be right-bottom
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(text=lambda: self.subject and self.subject.name or ""),
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")


def draw_activity_final_node(_box, context, _bounding_box):
    cr = context.cairo
    if stroke_color := context.style["color"]:
        cr.set_source_rgba(*stroke_color)

    inner_radius = 10
    outer_radius = 15
    r = outer_radius

    d = r * 2
    path_ellipse(cr, r, r, d, d)
    cr.set_line_width(0.01)
    cr.set_line_width(2)
    stroke(context)

    d = inner_radius * 2
    path_ellipse(cr, r, r, d, d)
    cr.set_line_width(0.01)
    cr.fill()


@represents(UML.FlowFinalNode)
class FlowFinalNodeItem(ActivityNodeItem, ElementPresentation):
    """Representation of flow final node.

    Flow final node has name which is put near right-bottom side of
    node.
    """

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=20, height=20)
        no_movable_handles(self)

        self.shape = IconBox(
            Box(draw=draw_flow_final_node),
            # Text should be right-bottom
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(text=lambda: self.subject and self.subject.name or ""),
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")


def draw_flow_final_node(_box, context, _bounding_box):
    cr = context.cairo
    r = 10
    d = r * 2
    path_ellipse(cr, r, r, d, d)
    stroke(context)

    dr = (1 - math.sin(math.pi / 4)) * r
    cr.move_to(dr, dr)
    cr.line_to(d - dr, d - dr)
    cr.move_to(dr, d - dr)
    cr.line_to(d - dr, dr)
    stroke(context, fill=False)


@represents(UML.DecisionNode)
class DecisionNodeItem(ActivityNodeItem, ElementPresentation):
    """Representation of decision or merge node."""

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id, width=20, height=30)
        no_movable_handles(self)

        self.shape = IconBox(
            Box(draw=draw_decision_node),
            # Text should be left-top
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(text=self.node_type, style={"font-size": "small"}),
            Text(text=lambda: self.subject and self.subject.name or ""),
        )

        self.watch("show_underlaying_type")
        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")

    show_underlaying_type: attribute[int] = attribute("show_type", int, 0)
    combined: relation_one[UML.ControlNode] = association(
        "combined", UML.ControlNode, upper=1
    )

    def node_type(self):
        if not self.show_underlaying_type:
            return ""
        if self.combined:
            return gettext("merge/decision")
        elif isinstance(self.subject, UML.MergeNode):
            return gettext("merge")
        elif isinstance(self.subject, UML.DecisionNode):
            return gettext("decision")
        return ""


def draw_decision_node(_box, context, _bounding_box):
    """Draw diamond shape, which represents decision and merge nodes."""
    cr = context.cairo
    r = 15
    r2 = r * 2 / 3

    cr.move_to(r2, 0)
    cr.line_to(r2 * 2, r)
    cr.line_to(r2, r * 2)
    cr.line_to(0, r)
    cr.close_path()
    stroke(context)


@represents(UML.ForkNode)
class ForkNodeItem(Named, Presentation[UML.ForkNode], HandlePositionUpdate):
    """Representation of fork and join node."""

    def __init__(self, diagram, id=None):
        super().__init__(diagram, id=id)

        h1, h2 = Handle(), Handle()
        self._handles = [h1, h2]
        self._ports = [LinePort(h1.pos, h2.pos)]
        self.watch_handle(h1)
        self.watch_handle(h2)

        self.shape = IconBox(
            Box(draw=self.draw_fork_node),
            Text(
                text=lambda: stereotypes_str(self.subject),
            ),
            Text(text=lambda: self.subject and self.subject.name or ""),
            Text(
                text=lambda: isinstance(self.subject, UML.JoinNode)
                and self.subject.joinSpec not in (None, DEFAULT_JOIN_SPEC)
                and f"{{ joinSpec = {self.subject.joinSpec} }}"
                or "",
            ),
        )

        self.watch("subject[NamedElement].name")
        self.watch("subject.appliedStereotype.classifier.name")
        self.watch("subject[JoinNode].joinSpec")

        diagram.connections.add_constraint(self, constraint(vertical=(h1.pos, h2.pos)))
        diagram.connections.add_constraint(
            self, constraint(above=(h1.pos, h2.pos), delta=30)
        )

    combined: relation_one[UML.ControlNode] = association(
        "combined", UML.ControlNode, upper=1
    )

    def handles(self):
        return self._handles

    def ports(self):
        return self._ports

    def save(self, save_func):
        m = Matrix(*self.matrix)
        m.translate(0, self._handles[0].pos.y)
        save_func("matrix", tuple(m))
        save_func("height", float(self._handles[1].pos.y - self._handles[0].pos.y))
        super().save(save_func)

    def load(self, name, value):
        if name == "height":
            self._handles[1].pos.y = ast.literal_eval(value)
        else:
            super().load(name, value)

    def draw(self, context):
        h1, h2 = self._handles
        height = h2.pos.y - h1.pos.y
        self.shape.draw(context, Rectangle(0, 0, 1, height))

    def draw_fork_node(self, _box, context, _bounding_box):
        """
        Draw vertical line - symbol of fork and join nodes. Join
        specification is also drawn above the item.
        """
        cr = context.cairo

        cr.set_line_width(6)
        if stroke := context.style.get("color"):
            cr.set_source_rgba(*stroke)
        h1, h2 = self._handles
        cr.move_to(h1.pos.x, h1.pos.y)
        cr.line_to(h2.pos.x, h2.pos.y)
        cr.stroke()

    def point(self, x, y):
        h1, h2 = self._handles
        d, p = distance_line_point(h1.pos, h2.pos, (x, y))
        # Subtract line_width / 2
        return d - 3
