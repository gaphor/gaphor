"""
Activity control nodes.
"""

import math

from gaphas.util import path_ellipse

from gaphor import UML
from gaphor import resource
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_CENTER, ALIGN_TOP, \
        ALIGN_RIGHT, ALIGN_BOTTOM
from gaphor.diagram.style import get_text_point
from gaphas.util import text_extents


class ActivityNodeItem(NamedItem):
    """Basic class for simple activity nodes.
    Simple activity node is not resizable.
    """
    __style__   = {
        'name-outside': True,
        'name-padding': (2, 2, 2, 2),
    }

    def __init__(self, id=None, width=0, height=0):
        NamedItem.__init__(self, id, width, height)
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
        'name-align': (ALIGN_LEFT, ALIGN_TOP),
    }
    
    RADIUS = 10

    def __init__(self, id = None, width = 20, height = 20):
        ActivityNodeItem.__init__(self, id, width, height)

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
        'name-align': (ALIGN_RIGHT, ALIGN_BOTTOM),
    }

    RADIUS_1 = 10
    RADIUS_2 = 15

    def __init__(self, id=None, width=30, height=30):
        ActivityNodeItem.__init__(self, id, width, height)

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
        'name-align': (ALIGN_RIGHT, ALIGN_BOTTOM),
    }

    RADIUS = 10

    def __init__(self, id=None, width=20, height=20):
        ActivityNodeItem.__init__(self, id, width, height)

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
        


class FDNode(ActivityNodeItem):
    """Abstract class for fork and decision UI nodes. These nodes contain
    combined property, which determines if the they represent combination
    of fork/join or decision/merge nodes as described in UML
    specification.
    """

    def __init__(self, id, width, height):
        ActivityNodeItem.__init__(self, id, width, height)
        self._combined = False
        self.set_prop_persistent('combined')


    def do_set_property(self, pspec, value):
        if pspec.name == 'combined':
            self.preserve_property('combined')
            self._combined = value
        else:
            ActivityNodeItem.do_set_property(self, pspec, value)


    def do_get_property(self, pspec):
        if pspec.name == 'combined':
            return self._combined
        else:
            return ActivityNodeItem.do_get_property(self, pspec)



class DecisionNodeItem(FDNode):
    """
    Representation of decision or merge node.
    """

    __uml__   = UML.DecisionNode
    __style__   = {
        'name-align': (ALIGN_LEFT, ALIGN_TOP),
    }

    RADIUS = 15

    def __init__(self, id=None, width = 20, height = 30):
        FDNode.__init__(self, id, width, height)

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

        super(FDNode, self).draw(context)



class ForkNodeItem(FDNode):
    """
    Representation of fork and join node.
    """
    __uml__   = UML.JoinNode
    #__uml__   = UML.ForkNode
    __style__ = {
        'name-align': (ALIGN_CENTER, ALIGN_BOTTOM),
    }

    def __init__(self, id = None, width = 6.0, height = 45.0):
#        GroupBase.__init__(self)
        FDNode.__init__(self, id, width, height)

        self._join_spec = 'join spec test'
        self._join_spec_x = 0
        self._join_spec_y = 0

#        for h in self.handles:
#            h.props.movable = False
#            h.props.visible = False
#        self.handles[diacanvas.HANDLE_N].props.visible = True
#        self.handles[diacanvas.HANDLE_S].props.visible = True
#        self.handles[diacanvas.HANDLE_N].props.movable = True
#        self.handles[diacanvas.HANDLE_S].props.movable = True

    def update(self, context):
        """
        Update join specification position.
        """
        self._join_spec_x, self._join_spec_y = get_text_point(
                text_extents(context.cairo, self._join_spec),
                self.width, self.height,
                (ALIGN_CENTER, ALIGN_TOP),
                (10, 0, 0, 0),
                True)


    def draw(self, context):
        """
        Draw vertical line - symbol of fork and join nodes. Join
        specification is also drawn above the item.
        """
        cr = context.cairo
        cr.set_line_width(self.width)
        cr.move_to(0, 0)
        cr.line_to(0, self.height)
        cr.move_to(self.name_x, self.name_y)

        cr.move_to(self._join_spec_x, self._join_spec_y)
        cr.show_text(self._join_spec)

        cr.stroke()
        super(ForkNodeItem, self).draw(context)


###    def on_update(self, affine):
###        """
###        Update fork/join node.
###
###        If node is join node then update also join specification.
###        """
###        FDNode.on_update(self, affine)
###
###        w, h = self._join_spec.get_size()
###        self._join_spec.update_label((self.width - w) / 2, 
###            -h - self.MARGIN)
###
###        GroupBase.on_update(self, affine)
###
###
###    def on_subject_notify(self, pspec, notifiers = ()):
###        """
###        Detect changes of subject.
###
###        If subject is join node, then set subject of join specification
###        text element.
###        """
###        FDNode.on_subject_notify(self, pspec, notifiers)
###        if self.subject and isinstance(self.subject, UML.JoinNode):
###            factory = resource(UML.ElementFactory)
###            if not self.subject.joinSpec:
###                self.subject.joinSpec = factory.create(UML.LiteralSpecification)
###                self.subject.joinSpec.value = 'and'
###            self._join_spec.subject = self.subject.joinSpec
###        else:
###            self._join_spec.subject = None
###        self.request_update()

# vim:sw=4:et
