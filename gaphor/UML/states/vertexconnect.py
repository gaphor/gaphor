"""Connection between two state machine vertices (state, pseudostate) using
transition.

To register connectors implemented in this module, it is imported in
gaphor.adapter package.
"""

from gaphor import UML
from gaphor.diagram.connectors import (
    Connector,
    DirectionalRelationshipConnect,
    RelationshipConnect,
)
from gaphor.UML.states.finalstate import FinalStateItem
from gaphor.UML.states.pseudostates import PseudostateItem
from gaphor.UML.states.state import StateItem
from gaphor.UML.states.transition import TransitionItem


class TransactionConnectMixin:
    """Abstract relationship between two state vertices."""

    def connect_subject(self: RelationshipConnect, handle):  # type: ignore[misc]
        relation = self.relationship_or_new(
            UML.Transition, UML.Transition.source, UML.Transition.target
        )
        region = self.get_connected(self.line.head).subject.container  # type: ignore[union-attr]
        relation.container = region
        self.line.subject = relation
        if relation.guard is None:
            relation.guard = self.line.model.create(UML.Constraint)


@Connector.register(StateItem, TransitionItem)
class StateTransitionConnect(TransactionConnectMixin, RelationshipConnect):
    """Connect two state vertices using transition item."""


@Connector.register(FinalStateItem, TransitionItem)
class VertexTransitionConnect(TransactionConnectMixin, DirectionalRelationshipConnect):
    """Connect two vertices using transition item."""

    def allow(self, handle, port):
        """Glue transition handle and vertex item.

        Guard against connecting transition's head with final state.
        """
        line = self.line
        subject = self.element.subject

        return (
            super().allow(handle, port)
            and isinstance(subject, UML.FinalState)
            and handle is line.tail
        )


@Connector.register(PseudostateItem, TransitionItem)
class PseudostateTransitionConnect(
    TransactionConnectMixin, DirectionalRelationshipConnect
):
    """Connect any number of incoming and outgoing transitions to a
    pseudostate."""
