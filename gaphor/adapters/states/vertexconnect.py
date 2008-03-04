"""
Connection between two state machine vertices (state, pseudostate) using
transition.

To register connectors implemented in this module, it is imported in
gaphor.adapter package.
"""

from zope import interface, component

from gaphor import UML
from gaphor.diagram import items
from gaphor.adapters.connectors import RelationshipConnect


class VertexConnect(RelationshipConnect):
    """
    Abstract relationship between two state vertices.
    """
    def connect_subject(self, handle):
        relation = self.relationship_or_new(UML.Transition,
                    ('source', 'outgoing'),
                    ('target', 'incoming'))
        self.line.subject = relation



class TransitionConnect(VertexConnect):
    """
    Connect two state vertices using transition item.
    """
    component.adapts(items.VertexItem, items.TransitionItem)

    def glue(self, handle):
        """
        Glue transition handle and vertex item. Guard from connecting
        transition's head with final state.
        """
        line = self.line
        subject = self.element.subject

        is_final = isinstance(subject, UML.FinalState)
        if isinstance(subject, UML.State) and not is_final \
                or handle is line.tail and is_final:
            return super(TransitionConnect, self).glue(handle)
        else:
            return None

component.provideAdapter(TransitionConnect)



class InitialPseudostateTransitionConnect(VertexConnect):
    """
    Connect initial pseudostate using transition item.

    It modifies InitialPseudostateItem._connected attribute to disallow
    connection of more than one transition.
    """
    component.adapts(items.InitialPseudostateItem, items.TransitionItem)

    def glue(self, handle):
        """
        Glue to initial pseudostate with transition's head and when there are
        no transitions connected.
        """
        line = self.line
        subject = self.element.subject

        if handle is line.head and not self.element._connected:
            return super(InitialPseudostateTransitionConnect, self).glue(handle)
        else:
            return None


    def connect(self, handle):
        """
        Update InitialPseudostateItem._connected attribute to `True` to
        disallow more connections.
        """
        if super(InitialPseudostateTransitionConnect, self).connect(handle):
            self.element._connected = True


    def disconnect(self, handle):
        """
        Update InitialPseudostateItem._connected attribute to `False` to
        allow transition connection again after disconnection.
        """
        super(InitialPseudostateTransitionConnect, self).disconnect(handle)
        self.element._connected = False

component.provideAdapter(InitialPseudostateTransitionConnect)
