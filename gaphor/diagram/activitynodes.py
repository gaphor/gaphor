"""
Activity control nodes.
"""

import math

from gaphas.util import path_ellipse, text_align
from gaphas.state import observed, reversible_property

from gaphor import UML
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_CENTER, ALIGN_TOP, \
        ALIGN_RIGHT, ALIGN_BOTTOM
from gaphor.diagram.style import get_text_point
from gaphas.util import text_extents


DEFAULT_JOIN_SPEC = 'and'


class ActivityNodeItem(NamedItem):
    """Basic class for simple activity nodes.
    Simple activity node is not resizable.
    """
    __style__   = {
        'name-outside': True,
        'name-padding': (2, 2, 2, 2),
    }

    def __init__(self, id=None):
        NamedItem.__init__(self, id)
        # Do not allow resizing of the node
        for h in self._handles:
            h.movable = False

        
class InitialNodeItem(ActivityNodeItem):
    """
    Representation of initial node. Initial node has name which is put near
    top-left side of node.
    """
    __uml__     = UML.InitialNode
    __style__   = {
        'min-size':   (20, 20),
        'name-align': (ALIGN_LEFT, ALIGN_TOP),
    }
    
    RADIUS = 10

    def draw(self, context):
        cr = context.cairo
        r = self.RADIUS
        d = r * 2
        path_ellipse(cr, r, r, d, d)
        cr.set_line_width(0.01)
        cr.fill()
        
        super(InitialNodeItem, self).draw(context)


class ActivityFinalNodeItem(ActivityNodeItem):
    """Representation of activity final node. Activity final node has name
    which is put near right-bottom side of node.
    """

    __uml__ = UML.ActivityFinalNode
    __style__   = {
        'min-size':   (30, 30),
        'name-align': (ALIGN_RIGHT, ALIGN_BOTTOM),
    }

    RADIUS_1 = 10
    RADIUS_2 = 15

    def draw(self, context):
        cr = context.cairo
        r = self.RADIUS_2 + 1
        d = self.RADIUS_1 * 2
        path_ellipse(cr, r, r, d, d)
        cr.set_line_width(0.01)
        cr.fill()

        d = r * 2
        path_ellipse(cr, r, r, d, d)
        cr.set_line_width(0.01)
        cr.set_line_width(2)
        cr.stroke()

        super(ActivityFinalNodeItem, self).draw(context)


class FlowFinalNodeItem(ActivityNodeItem):
    """
    Representation of flow final node. Flow final node has name which is
    put near right-bottom side of node.
    """

    __uml__ = UML.FlowFinalNode
    __style__   = {
        'min-size':   (20, 20),
        'name-align': (ALIGN_RIGHT, ALIGN_BOTTOM),
    }

    RADIUS = 10

    def draw(self, context):
        cr = context.cairo
        r = self.RADIUS
        d = r * 2
        path_ellipse(cr, r, r, d, d)
        cr.stroke()

        dr = (1 - math.sin(math.pi / 4)) * r
        cr.move_to(dr, dr)
        cr.line_to(d - dr, d - dr)
        cr.move_to(dr, d - dr)
        cr.line_to(d - dr, dr)
        cr.stroke()
        
        super(FlowFinalNodeItem, self).draw(context)
        


class ForkDecisionNodeItem(ActivityNodeItem):
    """
    Abstract class for fork and decision UI nodes. These nodes contain
    combined property, which determines if the they represent combination
    of fork/join or decision/merge nodes as described in UML
    specification.
    """

    def __init__(self, id=None):
        ActivityNodeItem.__init__(self, id)
        self._combined = None
        #self.set_prop_persistent('combined')

    def save(self, save_func):
        if self._combined:
            save_func('combined', self._combined, reference=True)
        super(ForkDecisionNodeItem, self).save(save_func)

    def load(self, name, value):
        if name == 'combined':
            self._combined = value
        else:
            super(ForkDecisionNodeItem, self).load(name, value)

    @observed
    def _set_combined(self, value):
        #self.preserve_property('combined')
        self._combined = value

    combined = reversible_property(lambda s: s._combined, _set_combined)
        

class DecisionNodeItem(ForkDecisionNodeItem):
    """
    Representation of decision or merge node.
    """

    __uml__   = UML.DecisionNode
    __style__   = {
        'min-size':   (20, 30),
        'name-align': (ALIGN_LEFT, ALIGN_TOP),
    }

    RADIUS = 15

    def draw(self, context):
        """
        Draw diamond shape, which represents decision and merge nodes.
        """
        cr = context.cairo
        r = self.RADIUS
        r2 = r * 2/3

        cr.move_to(r2, 0)
        cr.line_to(r2 * 2, r)
        cr.line_to(r2, r * 2)
        cr.line_to(0, r)
        cr.close_path()
        cr.stroke()

        super(DecisionNodeItem, self).draw(context)



class ForkNodeItem(ForkDecisionNodeItem):
    """
    Representation of fork and join node.
    """
    __uml__   = UML.JoinNode
    #__uml__   = UML.ForkNode
    __style__ = {
        'min-size':   (6, 45),
        'name-align': (ALIGN_CENTER, ALIGN_BOTTOM),
    }

    def __init__(self, id=None):
        ForkDecisionNodeItem.__init__(self, id)
        self._join_spec = self.add_text('joinSpec.value',
            when = self.display_join_spec)


    def display_join_spec(self):
        """
        Check if join specification should be displayed.
        """
        return isinstance(self.subject, UML.JoinNode) \
            and self.subject.joinSpec.value != DEFAULT_JOIN_SPEC


    def draw(self, context):
        """
        Draw vertical line - symbol of fork and join nodes. Join
        specification is also drawn above the item.
        """
        cr = context.cairo
        cr.set_line_width(self.width)
        x = self.width / 2.0
        cr.move_to(x, 0)
        cr.line_to(x, self.height)

        cr.stroke()
        super(ForkNodeItem, self).draw(context)


    def on_subject_notify(self, pspec, notifiers = ()):
        """
        Detect changes of subject.

        If subject is join node, then set subject of join specification
        text element.
        """
        ForkDecisionNodeItem.on_subject_notify(self, pspec,
                ('joinSpec', 'joinSpec.value') + notifiers)
        self.set_join_spec(DEFAULT_JOIN_SPEC)
        self.request_update()


    def set_join_spec(self, value):
        """
        Set join specification.
        """
        subject = self.subject
        if not subject or not isinstance(subject, UML.JoinNode):
            return

        if not subject.joinSpec:
            subject.joinSpec = UML.create(UML.LiteralSpecification)

        if not value:
            value = DEFAULT_JOIN_SPEC

        subject.joinSpec.value = value
        self._join_spec.text = value


    def on_subject_notify__joinSpec(self, subject, pspec=None):
        self.request_update()


    def on_subject_notify__joinSpec_value(self, subject, pspec=None):
        self.request_update()


# vim:sw=4:et
