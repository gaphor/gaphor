'''
ControlFlow and ObjectFlow -- 
'''
# vim:sw=4:et:ai

from __future__ import generators

import diacanvas

from gaphor import resource
from gaphor import UML
from gaphor.diagram import initialize_item, TextElement
from gaphor.diagram.relationship import RelationshipItem

from gaphor.diagram.groupable import GroupBase
import gaphor.diagram.util


class FlowItem(RelationshipItem, GroupBase):
    def __init__(self, id = None):
        GroupBase.__init__(self, {
            '_name': TextElement('name'),
            '_guard': TextElement('value'),
        })

        RelationshipItem.__init__(self, id)

        self.set(has_tail=1, tail_fill_color=0,
                 tail_a=0.0, tail_b=15.0, tail_c=6.0, tail_d=6.0)

        isinstance(self._guard, TextElement)
        isinstance(self._name, TextElement)


    def on_subject_notify(self, pspec, notifiers = ()):
        RelationshipItem.on_subject_notify(self, pspec, notifiers)
        if self.subject:
            self._guard.subject = self.subject.guard
        else:
            self._guard.subject = None
        self._name.subject = self.subject
        self.request_update()


    def on_update (self, affine):
        RelationshipItem.on_update(self, affine)
        handles = self.handles
        middle = len(handles)/2

        def get_pos_centered(p1, p2, width, height):
            x = p1[0] > p2[0] and width + 2 or -2
            x = (p1[0] + p2[0]) / 2.0 - x
            y = p1[1] <= p2[1] and height or 0
            y = (p1[1] + p2[1]) / 2.0 - y
            return x, y

        def get_pos(p1, p2, width, height):
            x = p1[0] > p2[0] and -10 or width + 10
            x = p2[0] - x
            y = p1[1] <= p2[1] and height + 15 or -15
            y = p2[1] - y
            return x, y

        w, h = self._guard.get_size()
        x, y = get_pos_centered(handles[middle-1].get_pos_i(),
            handles[middle].get_pos_i(),
            w, h)
        self._guard.update_label(x, y)

        w, h = self._name.get_size()
        x, y = get_pos(handles[-2].get_pos_i(),
            handles[-1].get_pos_i(),
            w, h)
        self._name.update_label(x, y)

        GroupBase.on_update(self, affine)


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

    def confirm_connect_handle (self, handle):
        """See RelationshipItem.confirm_connect_handle().
        """
        c1 = self.handles[0].connected_to   # source
        c2 = self.handles[-1].connected_to  # target
        if c1 and c2:
            s1 = c1.subject
            if isinstance(s1, tuple(gaphor.diagram.util.node_classes.keys())) and c1.combined:
                log.debug('getting combined node for flow source')
                s1 = s1.outgoing[0].target

            s2 = c2.subject
            relation = self.find_relationship(s1, s2)
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


    def confirm_disconnect_handle (self, handle, was_connected_to):
        """See RelationshipItem.confirm_disconnect_handle().
        """
        c1 = self.handles[0].connected_to   # source
        c2 = self.handles[-1].connected_to  # target

        if not c1:
            c1 = was_connected_to
        if not c2:
            c2 = was_connected_to

        self.set_subject(None)

        if c1:
            gaphor.diagram.util.determine_node_on_disconnect(c1)
        if c2:
            gaphor.diagram.util.determine_node_on_disconnect(c2)


initialize_item(FlowItem, UML.ControlFlow)
