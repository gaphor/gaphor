"""
Activity control nodes.
"""
from __future__ import print_function
from __future__ import division

from builtins import map
from past.utils import old_div
import math

from gaphas.util import path_ellipse
from gaphas.state import observed, reversible_property
from gaphas.item import Handle, Item, LinePort
from gaphas.constraint import EqualsConstraint, LessThanConstraint
from gaphas.geometry import distance_line_point

from gaphor import UML
from gaphor.core import inject
from gaphor.diagram.diagramitem import DiagramItem
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.style import ALIGN_LEFT, ALIGN_CENTER, ALIGN_TOP, \
        ALIGN_RIGHT, ALIGN_BOTTOM
from gaphor.diagram.style import get_text_point


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

        dr = (1 - math.sin(old_div(math.pi, 4))) * r
        cr.move_to(dr, dr)
        cr.line_to(d - dr, d - dr)
        cr.move_to(dr, d - dr)
        cr.line_to(d - dr, dr)
        cr.stroke()
        
        super(FlowFinalNodeItem, self).draw(context)
        


class DecisionNodeItem(ActivityNodeItem):
    """
    Representation of decision or merge node.
    """
    __uml__   = UML.DecisionNode
    __style__   = {
        'min-size':   (20, 30),
        'name-align': (ALIGN_LEFT, ALIGN_TOP),
    }

    RADIUS = 15

    def __init__(self, id=None):
        ActivityNodeItem.__init__(self, id)
        self._combined = None
        #self.set_prop_persistent('combined')

    def save(self, save_func):
        if self._combined:
            save_func('combined', self._combined, reference=True)
        super(DecisionNodeItem, self).save(save_func)

    def load(self, name, value):
        if name == 'combined':
            self._combined = value
        else:
            super(DecisionNodeItem, self).load(name, value)

    @observed
    def _set_combined(self, value):
        #self.preserve_property('combined')
        self._combined = value

    combined = reversible_property(lambda s: s._combined, _set_combined)
        
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



class ForkNodeItem(Item, DiagramItem):
    """
    Representation of fork and join node.
    """

    element_factory = inject('element_factory')

    __uml__   = UML.ForkNode

    __style__ = {
        'min-size':   (6, 45),
        'name-align': (ALIGN_CENTER, ALIGN_BOTTOM),
        'name-padding': (2, 2, 2, 2),
        'name-outside': True,
        'name-align-str': None,
    }

    STYLE_TOP = {
        'text-align': (ALIGN_CENTER, ALIGN_TOP),
        'text-outside': True,
    }

    def __init__(self, id=None):
        Item.__init__(self)
        DiagramItem.__init__(self, id)
        
        h1, h2 = Handle(), Handle()
        self._handles.append(h1)
        self._handles.append(h2)
        self._ports.append(LinePort(h1.pos, h2.pos))

        self._combined = None

        self._join_spec = self.add_text('joinSpec',
            pattern='{ joinSpec = %s }',
            style=self.STYLE_TOP,
            visible=self.is_join_spec_visible)

        self._name = self.add_text('name', style={
                    'text-align': self.style.name_align,
                    'text-padding': self.style.name_padding,
                    'text-outside': self.style.name_outside,
                    'text-align-str': self.style.name_align_str,
                    'text-align-group': 'stereotype',
                }, editable=True)

        self.watch('subject<NamedElement>.name', self.on_named_element_name)\
            .watch('subject<JoinNode>.joinSpec', self.on_join_node_join_spec)


    def save(self, save_func):
        save_func('matrix', tuple(self.matrix))
        save_func('height', float(self._handles[1].pos.y))
        if self._combined:
            save_func('combined', self._combined, reference=True)
        DiagramItem.save(self, save_func)

    def load(self, name, value):
        if name == 'matrix':
            self.matrix = eval(value)
        elif name == 'height':
            self._handles[1].pos.y = eval(value)
        elif name == 'combined':
            self._combined = value
        else:
            #DiagramItem.load(self, name, value)
            super(ForkNodeItem, self).load(name, value)

    def postload(self):
        subject = self.subject
        if subject and isinstance(subject, UML.JoinNode) and subject.joinSpec:
            self._join_spec.text = self.subject.joinSpec
        self.on_named_element_name(None)
        super(ForkNodeItem, self).postload()

    @observed
    def _set_combined(self, value):
        #self.preserve_property('combined')
        self._combined = value

    combined = reversible_property(lambda s: s._combined, _set_combined)

    def setup_canvas(self):
        super(ForkNodeItem, self).setup_canvas()
        self.register_handlers()

        h1, h2 = self._handles
        cadd = self.canvas.solver.add_constraint
        c1 = EqualsConstraint(a=h1.pos.x, b=h2.pos.x)
        c2 = LessThanConstraint(smaller=h1.pos.y, bigger=h2.pos.y, delta=30)
        self.__constraints = (cadd(c1), cadd(c2))
        list(map(self.canvas.solver.add_constraint, self.__constraints))


    def teardown_canvas(self):
        super(ForkNodeItem, self).teardown_canvas()
        list(map(self.canvas.solver.remove_constraint, self.__constraints))
        self.unregister_handlers()


    def is_join_spec_visible(self):
        """
        Check if join specification should be displayed.
        """
        return isinstance(self.subject, UML.JoinNode) \
            and self.subject.joinSpec is not None \
            and self.subject.joinSpec != DEFAULT_JOIN_SPEC


    def text_align(self, extents, align, padding, outside):
        h1, h2 = self._handles
        w, _ = self.style.min_size
        h = h2.pos.y - h1.pos.y
        x, y = get_text_point(extents, w, h, align, padding, outside)

        return x, y


    def pre_update(self, context):
        self.update_stereotype()
        Item.pre_update(self, context)
        DiagramItem.pre_update(self, context)


    def post_update(self, context):
        Item.post_update(self, context)
        DiagramItem.post_update(self, context)


    def draw(self, context):
        """
        Draw vertical line - symbol of fork and join nodes. Join
        specification is also drawn above the item.
        """
        Item.draw(self, context)
        DiagramItem.draw(self, context)

        cr = context.cairo

        cr.set_line_width(6)
        h1, h2 = self._handles
        cr.move_to(h1.pos.x, h1.pos.y)
        cr.line_to(h2.pos.x, h2.pos.y)

        cr.stroke()


    def point(self, pos):
        h1, h2 = self._handles
        d, p = distance_line_point(h1.pos, h2.pos, pos)
        # Substract line_width / 2
        return d - 3


    def on_named_element_name(self, event):
        print('on_named_element_name', self.subject)
        subject = self.subject
        if subject:
            self._name.text = subject.name
            self.request_update()

    def on_join_node_join_spec(self, event):
        subject = self.subject
        if subject:
            self._join_spec.text = subject.joinSpec or DEFAULT_JOIN_SPEC
            self.request_update()


def is_join_node(subject):
    """
    Check if ``subject`` is join node. 
    """
    return subject and isinstance(subject, UML.JoinNode)

# vim:sw=4:et
