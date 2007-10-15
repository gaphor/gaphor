"""
Connection between two state machine vertices (state, pseudostate) using
transition.
"""

from zope import interface, component

from gaphor.diagram import items
from gaphor.adapters.connectors import RelationshipConnect

class TransitionConnect(RelationshipConnect):
    """
    Connect two state vertices using transition item.
    """
    component.adapts(items.VertexItem, items.TransitionItem)

    def connect_subject(self, handle):
        relation = self.relationship_or_new(UML.Transition,
                    ('source', 'outgoing'),
                    ('target', 'incoming'))
        self.line.subject = relation

component.provideAdapter(TransitionConnect)
