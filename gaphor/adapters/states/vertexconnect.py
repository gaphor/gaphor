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
    def reconnect(self, handle, port):
         line = self.line
         c1 = self.get_connected(line.head)
         c2 = self.get_connected(line.tail)
         if line.head is handle:
             line.subject.source = c1.subject
         elif line.tail is handle:
             line.subject.target = c2.subject
         else:
             raise ValueError('Incorrect handle passed to adapter')


    def connect_subject(self, handle):
        relation = self.relationship_or_new(UML.Transition,
                    ('source', 'outgoing'),
                    ('target', 'incoming'))
        self.line.subject = relation
        if relation.guard is None:
            relation.guard = self.element_factory.create(UML.Constraint)
            relation.guard.specification = self.element_factory.create(UML.LiteralSpecification)



class TransitionConnect(VertexConnect):
    """
    Connect two state vertices using transition item.
    """
    component.adapts(items.VertexItem, items.TransitionItem)

    def allow(self, handle, port):
        """
        Glue transition handle and vertex item. Guard from connecting
        transition's head with final state.
        """
        line = self.line
        subject = self.element.subject

        is_final = isinstance(subject, UML.FinalState)
        if isinstance(subject, UML.State) and not is_final \
                or handle is line.tail and is_final:
            return super(TransitionConnect, self).allow(handle, port)
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

    def allow(self, handle, port):
        """
        Glue to initial pseudostate with transition's head and when there are
        no transitions connected.
        """
        line = self.line
        element = self.element
        subject = element.subject

        # Check if no other items are connected
        connections = self.canvas.get_connections(connected=element)
        connected_items = filter(lambda c: isinstance(c.item, items.TransitionItem) and c.item is not line, connections)
        if handle is line.head and not any(connected_items):
            return super(InitialPseudostateTransitionConnect, self).allow(handle, port)
        else:
            return None

component.provideAdapter(InitialPseudostateTransitionConnect)

class HistoryPseudostateTransitionConnect(VertexConnect):
    """
    Connect history pseudostate using transition item.

    It modifies InitialPseudostateItem._connected attribute to disallow
    connection of more than one transition.
    """
    component.adapts(items.HistoryPseudostateItem, items.TransitionItem)

    def allow(self, handle, port):
        """
        """
        return super(HistoryPseudostateTransitionConnect, self).allow(handle, port)

component.provideAdapter(HistoryPseudostateTransitionConnect)

# vim:sw=4:et:ai
