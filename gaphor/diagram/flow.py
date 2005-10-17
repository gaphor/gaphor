'''
ControlFlow and ObjectFlow -- 
'''
# vim:sw=4:et:ai

from __future__ import generators

import pango
import diacanvas

from gaphor import resource
from gaphor import UML
from gaphor.diagram import initialize_item
from gaphor.diagram.diagramitem import DiagramItem
from gaphor.diagram.relationship import RelationshipItem

class FlowItem(RelationshipItem, diacanvas.CanvasGroupable):

    def __init__(self, id=None):
        RelationshipItem.__init__(self, id)
        self.set(has_tail=1, tail_fill_color=0,
                 tail_a=0.0, tail_b=15.0, tail_c=6.0, tail_d=6.0)
        self._guard = FlowGuard()
        self._guard.set_child_of(self)

    def on_update (self, affine):
        RelationshipItem.on_update(self, affine)
        handles = self.handles
        middle = len(handles)/2
        self._guard.update_label(handles[middle-1].get_pos_i(),
                                 handles[middle].get_pos_i())
        self.update_child(self._guard, affine)

        b1 = self.bounds
        b2 = self._guard.get_bounds(self._guard.affine)
        self.set_bounds((min(b1[0], b2[0]), min(b1[1], b2[1]),
                         max(b1[2], b2[2]), max(b1[3], b2[3])))

    # Gaphor Connection Protocol

    def find_relationship(self, head_subject, tail_subject):
        """See RelationshipItem.find_relationship().
        """
        return self._find_relationship(head_subject, tail_subject,
                                       ('source', 'outgoing'),
                                       ('target', 'incoming'))

    def allow_connect_handle(self, handle, connecting_to):
        """See RelationshipItem.allow_connect_handle().
        """
        try:
            return isinstance(connecting_to.subject, UML.ActivityNode)
        except AttributeError:
            return 0

    def confirm_connect_handle (self, handle):
        """See RelationshipItem.confirm_connect_handle().
        """
        c1 = self.handles[0].connected_to
        c2 = self.handles[-1].connected_to
        if c1 and c2:
            s1 = c1.subject
            s2 = c2.subject
            relation = self.find_relationship(s1, s2)
            if not relation:
                factory = resource(UML.ElementFactory)

                # if we connect to object node than flow uml class should
                # ObjectFlow
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
            self._guard.subject = relation.guard

            # determine classes of nodes
            # - if there is no more than one incoming edge nor outgoing edge, then
            #   by default diamond represents decision node and line represents fork node
            # - if there is one incoming edge and second flow is attached with its head
            #   (creating second incoming edge) then subject of UI element is changed
            #   to merge or join node
            # - if there is more than one incoming edge and flow is detached
            #   from UI element, then subject of UI element is changed from merge/join to
            #   decision or fork
            def move_collection(src, target, name):
                # first make of copy of collection, because assigning
                # element to target collection moves this element
                for flow in list(getattr(src, name)):
                    getattr(target, name).append(flow)

            def check_node(src):
                if not isinstance(src, (UML.ForkNode, UML.JoinNode, UML.DecisionNode, UML.MergeNode)):
                    return src

                node = src
                if len(src.incoming) > 1:
                    # tcls: target node class
                    if isinstance(src, UML.ForkNode):
                        tcls = UML.JoinNode
                    elif isinstance(src, UML.DecisionNode):
                        tcls = UML.MergeNode

                    log.debug('changing %s to %s' % (src.__class__, tcls))

                    target = factory.create(tcls) # create target node
                    move_collection(src, target, 'incoming')

                    if len(src.outgoing) > 1:
                        log.debug('combining nodes')
                        flow = factory.create(UML.ControlFlow)
                        flow.source = target
                        flow.target = src
                    else:
                        move_collection(src, target, 'outgoing')
                        log.debug('deleting node %s', src)
                        #src.unlink()
                        #del src
                    node = target
                else:
                    log.debug('leaving node %s' % node)

                assert isinstance(node, (UML.ForkNode, UML.DecisionNode)) \
                    and len(node.incoming) <= 1 \
                    and len(node.outgoing) >= 0 \
                    or isinstance(node, (UML.JoinNode, UML.MergeNode)) \
                    and len(node.incoming) > 1 \
                    and len(node.outgoing) <= 1, \
                    'UML metamodel problem %s (%d, %d)' \
                    % (node, len(node.incoming), len(node.outgoing))

                return node

            #c1.set_subject(check_node(s1))
            #c2.set_subject(check_node(s2))




    def confirm_disconnect_handle (self, handle, was_connected_to):
        """See RelationshipItem.confirm_disconnect_handle().
        """
        self.set_subject(None)

    # Groupable

    def on_groupable_add(self, item):
        return 0

    def on_groupable_remove(self, item):
        '''Do not allow the name to be removed.'''
        return 1

    def on_groupable_iter(self):
        return iter([self._guard])


class FlowGuard(diacanvas.CanvasItem, diacanvas.CanvasEditable, DiagramItem):

    __gproperties__ = DiagramItem.__gproperties__
    __gsignals__ = DiagramItem.__gsignals__

    FONT='sans 10'

    def __init__(self, id=None):
        self.__gobject_init__()
        DiagramItem.__init__(self, id)
        self.set_flags(diacanvas.COMPOSITE)
        
        font = pango.FontDescription(self.FONT)
        self._name = diacanvas.shape.Text()
        self._name.set_font_description(font)
        self._name.set_wrap_mode(diacanvas.shape.WRAP_NONE)
        self._name.set_markup(False)
        self._name_border = diacanvas.shape.Path()
        self._name_border.set_color(diacanvas.color(128,128,128))
        self._name_border.set_line_width(1.0)
        #self._name.set_text('guard')
        self._name_bounds = (0, 0, 0, 0)

    # Ensure we call the right connect functions:
    connect = DiagramItem.connect
    disconnect = DiagramItem.disconnect
    notify = DiagramItem.notify

    def postload(self):
        DiagramItem.postload(self)

    def set_text(self):
        if self.subject:
            self._name.set_text(self.subject.value or '')
            self.request_update()

    def edit(self):
        self.start_editing(self._name)

    def on_subject_notify(self, pspec, notifiers=()):
        DiagramItem.on_subject_notify(self, pspec, notifiers + ('value',))
        self.set_text()
        self.request_update()

    def on_subject_notify__value(self, value, pspec):
        self.set_text()
        self.parent.request_update()

    def update_label(self, p1, p2):
        name_w, name_h = map(max, self._name.to_pango_layout(True).get_pixel_size(), (10, 10))

        x = p1[0] > p2[0] and name_w + 2 or -2
        x = (p1[0] + p2[0]) / 2.0 - x
        y = p1[1] <= p2[1] and name_h or 0
        y = (p1[1] + p2[1]) / 2.0 - y

        a = self.get_property('affine')
        self.set_property('affine', (a[0], a[1], a[2], a[3], x, y))

        # Now set with and height:
        self._name_bounds = (0,0,name_w, name_h)

    def on_update(self, affine):
        diacanvas.CanvasItem.on_update(self, affine)

        # bounds calculation
        b1 = self._name_bounds
        self._name_border.rectangle((b1[0], b1[1]), (b1[2], b1[3]))
        self.set_bounds(b1)

    def on_point(self, x, y):
        p = (x, y)
        drp = diacanvas.geometry.distance_rectangle_point
        return drp(self._name_bounds, p)

    def on_shape_iter(self):
        if self.subject:
            yield self._name
            if self.is_selected():
                yield self._name_border

    # Editable

    def on_editable_get_editable_shape(self, x, y):
        return self._name

    def on_editable_start_editing(self, shape):
        pass
        #self.preserve_property('name')

    def on_editable_editing_done(self, shape, new_text):
        if self.subject:
            self.subject.value = new_text
        #self.set_text()
        #log.info('editing done')

initialize_item(FlowItem, UML.ControlFlow)
initialize_item(FlowGuard)

