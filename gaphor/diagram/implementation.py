"""
Implementation of interface.
"""

from gaphor import resource
from gaphor import UML
from gaphor.diagram.diagramline import DiagramLine

class ImplementationItem(DiagramLine):

    __uml__          = UML.Implementation
    __relationship__ = 'contract', None, 'implementatingClassifier', 'implementation'

    default_look = {
        'dash': (7.0, 5.0),
        'has_head': 1,
        'head_fill_color': 0,
        'head_a': 15.0,
        'head_b': 15.0,
        'head_c': 10.0,
        'head_d': 10.0,
    }
    folded_interface_look = {
        'dash': (1.0,),
        'has_head': 0,
    }

    def __init__(self, id = None):
        DiagramLine.__init__(self, id)
        self.set(**self.default_look)


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


    def on_update(self, affine):
        # change look into solid line when connected to folded interface
        from gaphor.diagram.interface import InterfaceItem
        conn_to = self.handles[0].connected_to
        if isinstance(conn_to, InterfaceItem) \
           and conn_to.is_folded():
            self.set(**self.folded_interface_look)
        else:
            self.set(**self.default_look)

        DiagramLine.on_update(self, affine)

# vim:sw=4
