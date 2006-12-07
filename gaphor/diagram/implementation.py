"""
Implementation of interface.
"""

from gaphor import resource
from gaphor import UML
from gaphor.diagram.diagramline import DiagramLine

class ImplementationItem(DiagramLine):

    __uml__          = UML.Implementation

    def __init__(self, id = None):
        DiagramLine.__init__(self, id)
        self._solid = False 

    def update(self, context):
        # change look into solid line when connected to folded interface
        from gaphor.diagram.interface import InterfaceItem
        conn_to = self.head.connected_to
        if isinstance(conn_to, InterfaceItem) \
           and conn_to.is_folded():
            self._solid = True
        else:
            self._solid = False
        DiagramLine.update(self, context)

    def draw_head(self, context):
        cr = context.cairo
        cr.move_to(0, 0)
        if not self._solid:
            cr.set_dash((), 0)
            cr.line_to(15, -10)
            cr.line_to(15, 10)
            cr.close_path()
            cr.stroke()
            cr.move_to(15, 0)

    def draw(self, context):
        if not self._solid:
            context.cairo.set_dash((7.0, 5.0), 0)
        super(ImplementationItem, self).draw(context)

    def allow_connect_handle(self, handle, connecting_to):
        """Implementation can connect head to Interface and
        tail to BehavioredClassifier.
        """
        can_connect = False

        head = self.handles[0] 
        tail = self.handles[-1]

        if head is handle and isinstance(connecting_to.subject, UML.Interface):
            can_connect = True
        elif tail is handle and isinstance(connecting_to.subject, UML.BehavioredClassifier):
            can_connect = True

        assert not head.connected_to \
            or head.connected_to and isinstance(head.connected_to.subject, UML.Interface)
        assert not tail.connected_to or \
            tail.connected_to and isinstance(tail.connected_to.subject, UML.BehavioredClassifier)
        assert not head.connected_to or not tail.connected_to \
            or head.connected_to and tail.connected_to \
                and head.connected_to.subject != tail.connected_to.subject

        #print 'Implementation.allow_connect_handle:', can_connect
        return can_connect


    def confirm_connect_handle (self, handle):
        c1 = self.handles[0].connected_to
        c2 = self.handles[-1].connected_to
        if c1 and c2:
            s1 = c1.subject
            s2 = c2.subject
            relation = self.relationship
            if not relation:
                #print 'No relationship found'
                relation = resource(UML.ElementFactory).create(UML.Implementation)
                relation.contract = s1
                relation.implementatingClassifier = s2
            self.subject = relation


    def confirm_disconnect_handle (self, handle, was_connected_to):
        """
        See DiagramLine.confirm_disconnect_handle().
        """
        self.set_subject(None)


# vim:sw=4
