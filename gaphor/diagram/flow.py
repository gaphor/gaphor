"""
Control flow and object flow implementation. 

Contains also implementation to split flows using activity edge connectors.
"""
# vim:sw=4:et:ai

from __future__ import generators

import diacanvas

from gaphor import resource
from gaphor import UML
from gaphor.diagram import TextElement
from gaphor.diagram.diagramline import DiagramLine

import gaphor.diagram.util

import itertools


class FlowBase(DiagramLine):
    """
    Control flow and object flow abstract class. Allows to create flows
    with name and guard.
    """

    __uml__ = UML.ControlFlow
    __relationship__ = 'source', 'outgoing', 'target', 'incoming'

    def __init__(self, id = None):
        GroupBase.__init__(self)
        DiagramLine.__init__(self, id)

        self.set(has_tail=1, tail_fill_color=0,
                 tail_a=0.0, tail_b=15.0, tail_c=6.0, tail_d=6.0)


    def create_name(self):
        self._name  = TextElement('name')
        self.add(self._name)


    def create_guard(self):
        self._guard = TextElement('value')
        self.add(self._guard)


    def on_subject_notify(self, pspec, notifiers = ()):
        DiagramLine.on_subject_notify(self, pspec, notifiers)

        if hasattr(self, '_guard'):
            if self.subject:
                self._guard.subject = self.subject.guard
            else:
                self._guard.subject = None

        if hasattr(self, '_name'):
            self._name.subject = self.subject

        self.request_update()


    def update_name(self, affine):
        handles = self.handles

        def get_pos(p1, p2, width, height):
            x = p1[0] > p2[0] and -10 or width + 10
            x = p2[0] - x
            y = p1[1] <= p2[1] and height + 15 or -15
            y = p2[1] - y
            return x, y

        p1 = handles[-2].get_pos_i()
        p2 = handles[-1].get_pos_i()
        w, h = self._name.get_size()
        x, y = get_pos(p1, p2, w, h)
        self._name.update_label(x, y)


    def update_guard(self, affine):
        handles = self.handles
        middle = len(handles)/2

        def get_pos_centered(p1, p2, width, height):
            x = p1[0] > p2[0] and width + 2 or -2
            x = (p1[0] + p2[0]) / 2.0 - x
            y = p1[1] <= p2[1] and height or 0
            y = (p1[1] + p2[1]) / 2.0 - y
            return x, y

        p1 = handles[middle-1].get_pos_i()
        p2 = handles[middle].get_pos_i()
        w, h = self._guard.get_size()
        x, y = get_pos_centered(p1, p2, w, h)
        self._guard.update_label(x, y)


    def on_update(self, affine):
        DiagramLine.on_update(self, affine)
        GroupBase.on_update(self, affine)


    def allow_connect_handle(self, handle, connecting_to):
        """See DiagramLine.allow_connect_handle().
        """
        can_connect = False

        subject = connecting_to.subject
        if isinstance(subject, UML.ActivityNode):
            source = self.handles[0] 
            target = self.handles[-1]

            # forbid flow source to connect to final node
            # forbid flow target to connect to initial nodes
            can_connect = True
            if source is handle and isinstance(subject, UML.FinalNode) \
                    or target is handle and isinstance(subject, UML.InitialNode):
                can_connect = False

        return can_connect


    def connect_items(self, c1, c2):
        if c1 and c2:
            s1 = c1.subject
            if isinstance(s1, tuple(gaphor.diagram.util.node_classes.keys())) \
                    and c1.props.combined:
                log.debug('getting combined node for flow source')
                s1 = s1.outgoing[0].target

            s2 = c2.subject
            relation = self.relationship
            if not relation:
                factory = resource(UML.ElementFactory)

                # if we connect to object node than flow uml class should
                # be ObjectFlow
                if isinstance(s1, UML.ObjectNode) \
                        or isinstance(s2, UML.ObjectNode):
                    relcls = UML.ObjectFlow
                else:
                    relcls = UML.ControlFlow
                assert relcls == UML.ObjectFlow or relcls == UML.ControlFlow

                relation = factory.create(relcls)
                relation.source = s1
                relation.target = s2
                relation.guard = factory.create(UML.LiteralSpecification)
            self.subject = relation

            gaphor.diagram.util.determine_node_on_connect(c1)
            gaphor.diagram.util.determine_node_on_connect(c2)


    def disconnect_items(self, c1, c2, was_connected_to):
        if not c1:
            c1 = was_connected_to
        if not c2:
            c2 = was_connected_to

        self.set_subject(None)

        if c1:
            gaphor.diagram.util.determine_node_on_disconnect(c1)
        if c2:
            gaphor.diagram.util.determine_node_on_disconnect(c2)



class FlowItem(FlowBase):
    """
    Representation of control flow and object flow. Flow item has name and
    guard. It can be splitted into two flows with activity edge connectors.
    """

    popup_menu = DiagramLine.popup_menu + (
        'separator',
        'SplitFlow',
    )

    def __init__(self, id = None):
        FlowBase.__init__(self, id)

        self.create_name()
        self.create_guard()


    def on_update(self, affine):
        self.update_name(affine)
        self.update_guard(affine)
        FlowBase.on_update(self, affine)


    # Gaphor Connection Protocol

    def confirm_connect_handle (self, handle):
        """See DiagramLine.confirm_connect_handle().
        """
        c1 = self.handles[0].connected_to   # source
        c2 = self.handles[-1].connected_to  # target
        self.connect_items(c1, c2)


    def confirm_disconnect_handle (self, handle, was_connected_to):
        """See DiagramLine.confirm_disconnect_handle().
        """
        c1 = self.handles[0].connected_to   # source
        c2 = self.handles[-1].connected_to  # target
        self.disconnect_items(c1, c2, was_connected_to)



class ACItem(TextElement):
    """
    Activity edge connector. It is a circle with name inside.
    """

    RADIUS = 10
    def __init__(self, id):
        TextElement.__init__(self, id)
        self._circle = diacanvas.shape.Ellipse()
        self._circle.set_line_width(2.0)
        self._circle.set_fill_color(diacanvas.color(255, 255, 255))
        self._circle.set_fill(diacanvas.shape.FILL_SOLID)
        self.show_border = False

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


    def on_shape_iter(self):
        """
        Return activity edge name and circle.
        """
        it = TextElement.on_shape_iter(self)
        return itertools.chain([self._circle], it)



class CFlowItem(FlowBase):
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
        FlowBase.__init__(self, id)

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
        FlowBase.save(self, save_func)
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
            FlowBase.load(self, name, value)


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
        x, y = gaphor.diagram.util.rotate(p1, p2, x, y, p1[0], p1[1])

        self._connector.move_center(x, y)

        FlowBase.on_update(self, affine)


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
        return FlowBase.allow_connect_handle(self, handle, connecting_to)


    def confirm_disconnect_handle (self, handle, was_connected_to):
        """See DiagramLine.confirm_disconnect_handle().
        """
        c1 = self.get_active_handle().connected_to             # source
        c2 = self._opposite.get_active_handle().connected_to   # target
        self.disconnect_items(c1, c2, was_connected_to)
        self._opposite.set_subject(None)



class CFlowItemA(CFlowItem):
    """
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
