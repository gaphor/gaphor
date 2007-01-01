"""
Control flow and object flow implementation. 

Contains also implementation to split flows using activity edge connectors.
"""

from math import atan, pi, sin, cos

from gaphor import resource

from gaphor import UML
from gaphor.diagram.diagramline import DiagramLine
from gaphas.geometry import Rectangle
from gaphas.util import text_extents, text_multiline
from gaphas.geometry import distance_rectangle_point


node_classes = {
    UML.ForkNode:     UML.JoinNode,
    UML.DecisionNode: UML.MergeNode,
    UML.JoinNode:     UML.ForkNode,
    UML.MergeNode:    UML.DecisionNode,
}


class FlowItem(DiagramLine):
    """
    Representation of control flow and object flow. Flow item has name and
    guard. It can be splitted into two flows with activity edge connectors.
    """

    __uml__ = UML.ControlFlow

    popup_menu = DiagramLine.popup_menu + (
        'separator',
        'SplitFlow',
    )

    def __init__(self, id = None):
        DiagramLine.__init__(self, id)
        self._name_bounds = None
        self._guard_bounds = None

        #self.set(has_tail=1, tail_fill_color=0,
        #         tail_a=0.0, tail_b=15.0, tail_c=6.0, tail_d=6.0)

    name_bounds = property(lambda s: s._name_bounds)
    guard_bounds = property(lambda s: s._guard_bounds)

    def on_subject_notify(self, pspec, notifiers = ()):
        DiagramLine.on_subject_notify(self, pspec, ('guard', 'guard.value',) + notifiers)

        self.request_update()

    def on_subject_notify__guard(self, subject, pspec=None):
        self.request_update()

    def on_subject_notify__guard_value(self, subject, pspec=None):
        self.request_update()

    def update_name(self, context):
        handles = self._handles

        def get_pos(p1, p2, width, height):
            x = p1[0] > p2[0] and -10 or width + 10
            x = p2[0] - x
            y = p1[1] <= p2[1] and height + 5 or -15
            y = p2[1] - y
            return x, y

        p1 = handles[-2].pos
        p2 = handles[-1].pos
        w, h = text_extents(context.cairo, self.subject and self.subject.name)
        x, y = get_pos(p1, p2, w, h)
        self._name_bounds = Rectangle(x, y, width=max(10, w), height=max(10, h))


    def update_guard(self, context):
        handles = self._handles
        middle = len(handles)/2

        def get_pos_centered(p1, p2, width, height):
            x = p1[0] > p2[0] and width + 2 or -2
            x = (p1[0] + p2[0]) / 2.0 - x
            y = p1[1] <= p2[1] and height or 0
            y = (p1[1] + p2[1]) / 2.0 - y
            return x, y

        p1 = handles[middle-1].pos
        p2 = handles[middle].pos
        w, h = text_extents(context.cairo, self.subject and self.subject.guard and self.subject.guard.value)
        x, y = get_pos_centered(p1, p2, w, h)
        self._guard_bounds = Rectangle(x, y, width=max(10, w), height=max(10, h))


    def update(self, context):
        super(FlowItem, self).update(context)
        self.update_name(context)
        self.update_guard(context)

    def point(self, x, y):
        d1 = super(FlowItem, self).point(x, y)
        drp = distance_rectangle_point
        d2 = drp(self._name_bounds, (x, y))
        d3 = drp(self._guard_bounds, (x, y))
        return min(d1, d2, d3)

    def draw_tail(self, context):
        cr = context.cairo
        cr.line_to(0, 0)
        cr.stroke()
        cr.move_to(15, -6)
        cr.line_to(0, 0)
        cr.line_to(15, 6)

    def draw(self, context):
        super(FlowItem, self).draw(context)
        cr= context.cairo
        if self.subject:
            text_multiline(cr, self._name_bounds[0], self._name_bounds[3], self.subject.name)
            text_multiline(cr, self._guard_bounds[0], self._guard_bounds[3], self.subject.guard and self.subject.guard.value)

        if context.hovered or context.focused or context.draw_all:
            cr.set_line_width(0.5)
            b = self._name_bounds
            cr.rectangle(b.x0, b.y0, b.width, b.height)
            cr.stroke()
            b = self._guard_bounds
            cr.rectangle(b.x0, b.y0, b.width, b.height)
            cr.stroke()

        
#class ACItem(TextElement):
class ACItem(object):
    """
    Activity edge connector. It is a circle with name inside.
    """

    RADIUS = 10
    def __init__(self, id):
        #TextElement.__init__(self, id)
        #self._circle = diacanvas.shape.Ellipse()
        #self._circle.set_line_width(2.0)
        #self._circle.set_fill_color(diacanvas.color(255, 255, 255))
        #self._circle.set_fill(diacanvas.shape.FILL_SOLID)
        #self.show_border = False

        # set new value notification function to change activity edge
        # connector name globally
        vnf = self.on_subject_notify__value
        def f(subject, pspec):
            vnf(subject, pspec)
            if self.parent._opposite:
                self.parent._opposite._connector.subject.value = subject.value
        self.on_subject_notify__value = f


    def move_center(self, x, y):
        """
        Move center of item to point (x, y). Other parts of item are
        aligned to this point.
        """
        a = self.props.affine
        x -= self.RADIUS
        y -= self.RADIUS
        self.props.affine = (a[0], a[1], a[2], a[3], x, y)


    def on_update(self, affine):
        """
        Center name of activity edge connector and put a circle around it.
        """
        r = self.RADIUS * 2
        x = self.RADIUS
        y = self.RADIUS

        self._circle.ellipse(center = (x, y), width = r, height = r)

        # get label size and move it so it is centered with circle
        w, h = self.get_size()
        x, y = x - w / 2, y - h / 2
        self._name.set_pos((x, y))
        self._name_bounds = (x, y, x + w, y + h)

        TextElement.on_update(self, affine)

        self.set_bounds((-1, -1, r + 1, r + 1))


    def update_label(self, x, y):
        """
        Do nothing, use move_center method.
        """
        pass


class CFlowItem(FlowItem):
    """
    Abstract class for flows with activity edge connector. Flow with
    activity edge connector references other one, which has activity edge
    connector with same name (it is called opposite one).

    Such flows have active and inactive ends. Active end is connected to
    any node and inactive end is connected only to activity edge connector.
    """

    popup_menu = DiagramLine.popup_menu + (
        'separator',
        'MergeFlow',
    )

    def __init__(self, id = None):
        FlowItem.__init__(self, id)

        self._connector = ACItem('value')

        factory = resource(UML.ElementFactory)
        self._connector.subject = factory.create(UML.LiteralSpecification)
        self.add(self._connector)

        self._opposite = None

        # when flow item with connector is deleted, then kill opposite, too
        self.unlink_handler_id = self.connect('__unlink__', self.kill_opposite)


    def kill_opposite(self, source, name):
        # do not allow to be killed by opposite
        self._opposite.disconnect(self._opposite.unlink_handler_id)
        self._opposite.unlink()


    def save(self, save_func):
        """
        Save connector name and opposite flow with activity edge connector.
        """
        FlowItem.save(self, save_func)
        save_func('opposite', self._opposite, True)
        save_func('connector-name', self._connector.subject.value)


    def load(self, name, value):
        """
        Load connector name and opposite flow with activity edge connector.
        """
        if name == 'connector-name':
            self._connector.subject.value = value
        elif name == 'opposite':
            self._opposite = value
        else:
            FlowItem.load(self, name, value)


    def on_update(self, affine):
        """
        Draw flow line and activity edge connector.
        """
        # get parent line points to determine angle
        # used to rotate position of activity edge connector
        p1, p2 = self.get_line()

        # calculate position of connector center
        r = self._connector.RADIUS
        #x = p1[0] < p2[0] and r or -r
        x = p1[0] < p2[0] and -r or r
        y = 0
        x, y = rotate(p1, p2, x, y, p1[0], p1[1])

        self._connector.move_center(x, y)

        FlowItem.on_update(self, affine)


    def confirm_connect_handle(self, handle):
        """See DiagramLine.confirm_connect_handle().
        """
        c1 = self.get_active_handle().connected_to            # source
        c2 = self._opposite.get_active_handle().connected_to  # target

        # set correct relationship between connected items;
        # it should be (source, target) not (target, source);
        # otherwise we are looking for non-existing or wrong relationship
        if isinstance(self, CFlowItemB):
            c1, c2 = c2, c1

        self.connect_items(c1, c2)
        self._opposite.set_subject(self.subject)


    def allow_connect_handle(self, handle, connecting_to):
        if handle == self.get_inactive_handle():
            return False
        return FlowItem.allow_connect_handle(self, handle, connecting_to)


    def confirm_disconnect_handle (self, handle, was_connected_to):
        """See DiagramLine.confirm_disconnect_handle().
        """
        c1 = self.get_active_handle().connected_to             # source
        c2 = self._opposite.get_active_handle().connected_to   # target
        self.disconnect_items(c1, c2, was_connected_to)
        self._opposite.set_subject(None)



class CFlowItemA(CFlowItem):
    """
    * Is used for split flows, as is CFlowItemB *

    Flow with activity edge connector, which starts from node and points to
    activity edge connector.
    """
    def __init__(self, id):
        CFlowItem.__init__(self, id)
        self.create_guard()


    def on_update(self, affine):
        self.update_guard(affine)
        CFlowItem.on_update(self, affine)


    def get_line(self):
        p1 = self.handles[-1].get_pos_i()
        p2 = self.handles[-2].get_pos_i()
        return p1, p2


    def get_active_handle(self):
        """
        Return source handle as active one.
        """
        return self.handles[0]


    def get_inactive_handle(self):
        """
        Return target handle as inactive one.
        """
        return self.handles[-1]



class CFlowItemB(CFlowItem):
    """
    Flow with activity edge connector, which starts from activity edge
    connector and points to a node.
    """
    def __init__(self, id):
        CFlowItem.__init__(self, id)
        self.create_name()


    def on_update(self, affine):
        self.update_name(affine)
        CFlowItem.on_update(self, affine)


    def get_line(self):
        p1 = self.handles[0].get_pos_i()
        p2 = self.handles[1].get_pos_i()
        return p1, p2


    def get_active_handle(self):
        """
        Return target handle as active one.
        """
        return self.handles[-1]


    def get_inactive_handle(self):
        """
        Return source handle as inactive one.
        """
        return self.handles[0]




def move_collection(src, target, name):
    """
    Copy collection from one object to another.

    src    - source object
    target - target object
    name   - name of attribute, which is collection to copy
    """
    # first make of copy of collection, because assigning
    # element to target collection moves this element
    for flow in list(getattr(src, name)):
        getattr(target, name).append(flow)


def is_fd(node):
    """
    Check if node is fork or decision node.
    """
    return isinstance(node, (UML.ForkNode, UML.DecisionNode))


def change_node_class(node):
    """
    If UML constraints for fork, join, decision and merge nodes are not
    met, then create new node depending on input node class, i.e. create
    fork node from join node or merge node from decision node.

    If constraints are met, then return node itself.
    """
    if is_fd(node) and len(node.incoming) > 1 \
            or not is_fd(node) and len(node.incoming) < 2:

        factory = resource(UML.ElementFactory)
        cls = node_classes[node.__class__]
        log.debug('creating %s' % cls)
        nn = factory.create(cls)
        move_collection(node, nn, 'incoming')
        move_collection(node, nn, 'outgoing')
    else:
        nn = node

    assert nn is not None

    # we have to accept zero of outgoing edges in case of fork/descision
    # nodes
    assert is_fd(nn) and len(nn.incoming) <= 1 \
        or not is_fd(nn) and len(nn.incoming) >= 1, '%s' % nn
    assert is_fd(nn) and len(nn.outgoing) >= 0 \
        or not is_fd(nn) and len(nn.outgoing) <= 1, '%s' % nn
    return nn


def combine_nodes(node):
    """
    Create fork/join (decision/merge) nodes combination as described in UML
    specification.
    """
    log.debug('combining nodes')

    cls = node_classes[node.__class__]
    log.debug('creating %s' % cls)
    factory = resource(UML.ElementFactory)
    target = factory.create(cls)

    source = node
    if is_fd(node):
        source = target
        move_collection(node, target, 'incoming')

        # create new fork node
        cls = node_classes[target.__class__]
        log.debug('creating %s' % cls)
        target = factory.create(cls)
        move_collection(node, target, 'outgoing')
    else:
        # fork node is created, referenced by target
        move_collection(node, target, 'outgoing')

    assert not is_fd(source)
    assert is_fd(target)

    # create flow
    c1 = count_object_flows(source, 'incoming')
    c2 = count_object_flows(target, 'outgoing')

    if c1 > 0 or c2 > 0:
        flow = factory.create(UML.ControlFlow)
    else:
        flow = factory.create(UML.ObjectFlow)
    flow.source = source
    flow.target = target

    assert len(source.incoming) > 1
    assert len(source.outgoing) == 1

    assert len(target.incoming) == 1
    assert len(target.outgoing) > 1

    return source


def decombine_nodes(source):
    """
    Create node depending on source argument which denotes combination of
    fork/join (decision/merge) nodes as described in UML specification.

    Combination of nodes is destroyed.
    """
    log.debug('decombining nodes')
    flow = source.outgoing[0]
    target = flow.target

    if len(source.incoming) < 2:
        # create fork or decision
        cls = target.__class__
    else:
        # create join or merge
        cls = source.__class__

    factory = resource(UML.ElementFactory)
    node = factory.create(cls)

    move_collection(source, node, 'incoming')
    move_collection(target, node, 'outgoing')

    assert source != node

    # delete target and combining flow
    # source should be deleted by caller
    target.unlink()
    flow.unlink()

    # return new node
    return node


def determine_node_on_connect(el):
    """
    Determine classes of nodes depending on amount of incoming
    and outgoing edges. This method is called when flow is attached
    to node.

    If there is more than one incoming edge and more than one
    outgoing edge, then create two nodes and combine them with
    flow as described in UML specification.
    """
    subject = el.subject
    if not isinstance(subject, tuple(node_classes.keys())):
        return

    new_subject = subject

    if len(subject.incoming) > 1 and len(subject.outgoing) > 1:
        new_subject = combine_nodes(subject)
        el.props.combined = True

    else:
        new_subject = change_node_class(subject)

    change_node_subject(el, new_subject)

    if el.props.combined:
        check_combining_flow(el)


def determine_node_on_disconnect(el):
    """
    Determine classes of nodes depending on amount of incoming
    and outgoing edges. This method is called when flow is dettached
    from node.

    If there are combined nodes and there is no need for them, then replace
    combination with appropriate node (i.e. replace with fork node when
    there are less than two incoming edges). This way data model is kept as
    simple as possible.
    """
    subject = el.subject
    if not isinstance(subject, tuple(node_classes.keys())):
        return

    new_subject = subject

    if el.props.combined:
        cs = subject.outgoing[0].target
        # decombine node when there is no more than one incoming
        # and no more than one outgoing flow
        if len(subject.incoming) < 2 or len(cs.outgoing) < 2:
            new_subject = decombine_nodes(subject)
            el.props.combined = False
        else:
            check_combining_flow(el)

    else: 
        new_subject = change_node_class(subject)

    change_node_subject(el, new_subject)


def change_node_subject(el, new_subject):
    """
    Change element's subject if new subject is different than element's
    subject. If subject is changed, then old subject is destroyed.
    """
    subject = el.subject
    if new_subject != subject:
        log.debug('changing subject of ui node %s' % el)
        el.set_subject(new_subject)

        log.debug('deleting node %s' % subject)
        subject.unlink()


def create_flow(cls, flow):
    """
    Create new flow of class cls. Flow data from flow argument are copied
    to new created flow. Old flow is destroyed.
    """
    factory = resource(UML.ElementFactory)
    f = factory.create(cls)
    f.source = flow.source
    f.target = flow.target
    flow.unlink()
    return f


def count_object_flows(node, attr):
    """
    Count incoming or outgoing object flows.
    """
    return len(getattr(node, attr)
        .select(lambda flow: isinstance(flow, UML.ObjectFlow)))


def check_combining_flow(el):
    """
    Set object flow as combining flow when incoming or outgoing flow count
    is greater than zero. Otherwise change combining flow to control flow.
    """
    subject = el.subject
    flow = subject.outgoing[0] # combining flow
    combined = flow.target     # combined node

    c1 = count_object_flows(subject, 'incoming')
    c2 = count_object_flows(combined, 'outgoing')

    log.debug('combined incoming and outgoing object flow count: (%d, %d)' % (c1, c2))

    if (c1 > 0 or c2 > 0) and isinstance(flow, UML.ControlFlow):
        log.debug('changing combing flow to object flow')
        create_flow(UML.ObjectFlow, flow)
    elif c1 == 0 and c2 == 0 and isinstance(flow, UML.ObjectFlow):
        log.debug('changing combing flow to control flow')
        create_flow(UML.ControlFlow, flow)


def create_connector_end(connector, role):
    """
    Create Connector End, set role and attach created end to
    connector.
    """
    end = resource(UML.ElementFactory).create(UML.ConnectorEnd)
    end.role = role
    connector.end = end
    assert end in role.end
    return end


def rotate(p1, p2, a, b, x, y):
    """
    Rotate point (a, b) by angle, which is determined by line (p1, p2).

    Rotated point is moved by vector (x, y).
    """
    try:
        angle = atan((p1[1] - p2[1]) / (p1[0] - p2[0]))
    except ZeroDivisionError:
        da = p1[1] < p2[1] and 1.5 or -1.5
        angle = pi * da

    sin_angle = sin(angle)
    cos_angle = cos(angle)
    return (cos_angle * a - sin_angle * b + x,
            sin_angle * a + cos_angle * b + y)

# vim:sw=4:et:ai
