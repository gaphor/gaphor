"""Connection between two state machine vertices (state, pseudostate) using
transition.

To register connectors implemented in this module, it is imported in
gaphor.adapter package.
"""

from gaphor import UML
from gaphor.diagram.connectors import Connector, RelationshipConnect
from gaphor.UML.states.pseudostates import PseudostateItem
from gaphor.UML.states.state import VertexItem
from gaphor.UML.states.transition import TransitionItem


class VertexConnect(RelationshipConnect):
    """Abstract relationship between two state vertices."""

    def connect_subject(self, handle):
        relation = self.relationship_or_new(
            UML.Transition, UML.Transition.source, UML.Transition.target
        )
        region = self.get_connected(self.line.head).subject.container  # type: ignore[union-attr]
        relation.container = region
        self.line.subject = relation
        if relation.guard is None:
            relation.guard = self.line.model.create(UML.Constraint)


@Connector.register(VertexItem, TransitionItem)
class TransitionConnect(VertexConnect):
    """Connect two state vertices using transition item."""

    def allow(self, handle, port):
        """Glue transition handle and vertex item.

        Guard from connecting transition's head with final state.
        """
        line = self.line
        subject = self.element.subject

        is_final = isinstance(subject, UML.FinalState)
        if (
            isinstance(subject, UML.State)
            and not is_final
            or handle is line.tail
            and is_final
        ):
            return super().allow(handle, port)
        else:
            return None


@Connector.register(PseudostateItem, TransitionItem)
class PseudostateTransitionConnect(VertexConnect):
    """Connect pseudostate using transition item."""

    def allow(self, handle, port):
        """Glue to initial pseudostate with transition's head and when there
        are no transitions connected."""
        element = self.element
        assert isinstance(element.subject, UML.Pseudostate)

        if element.subject.kind != "initial":
            return super().allow(handle, port)

        # Check if no other items are connected
        connections = self.diagram.connections.get_connections(connected=element)
        line = self.line
        connected_items = [
            c
            for c in connections
            if isinstance(c.item, TransitionItem) and c.item is not line
        ]
        if handle is line.head and not any(connected_items):
            return super().allow(handle, port)
        else:
            return None
