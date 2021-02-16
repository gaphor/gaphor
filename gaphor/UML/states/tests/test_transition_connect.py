"""Test transition item and state vertices connections."""

from gaphor import UML
from gaphor.UML.states.finalstate import FinalStateItem
from gaphor.UML.states.pseudostates import PseudostateItem
from gaphor.UML.states.state import StateItem
from gaphor.UML.states.transition import TransitionItem


class TestTransitionConnector:
    def test_vertex_connect(self, case):
        """Test transition to state vertex connection."""
        v1 = case.create(StateItem, UML.State)
        v2 = case.create(StateItem, UML.State)

        t = case.create(TransitionItem)
        assert t.subject is None

        # connect vertices with transition
        case.connect(t, t.head, v1)
        case.connect(t, t.tail, v2)

        assert t.subject is not None

        assert len(case.kindof(UML.Transition)) == 1

        assert t.subject == v1.subject.outgoing[0]
        assert t.subject == v2.subject.incoming[0]
        assert t.subject.source == v1.subject
        assert t.subject.target == v2.subject

    def test_vertex_reconnect(self, case):
        """Test transition to state vertex reconnection."""
        v1 = case.create(StateItem, UML.State)
        v2 = case.create(StateItem, UML.State)
        v3 = case.create(StateItem, UML.State)

        t = case.create(TransitionItem)

        # connect: v1 -> v2
        case.connect(t, t.head, v1)
        case.connect(t, t.tail, v2)

        s = t.subject
        s.name = "tname"
        s.guard.specification = "tguard"

        # reconnect: v1 -> v3
        case.connect(t, t.tail, v3)

        assert s is t.subject
        assert len(case.kindof(UML.Transition)) == 1

        assert t.subject == v1.subject.outgoing[0]
        assert t.subject == v3.subject.incoming[0]
        assert t.subject.source == v1.subject
        assert t.subject.target == v3.subject

        assert len(v2.subject.incoming) == 0
        assert len(v2.subject.outgoing) == 0

    def test_vertex_disconnect(self, case):
        """Test transition and state vertices disconnection."""
        t = case.create(TransitionItem)
        v1 = case.create(StateItem, UML.State)
        v2 = case.create(StateItem, UML.State)

        case.connect(t, t.head, v1)
        case.connect(t, t.tail, v2)
        assert t.subject is not None

        assert len(case.kindof(UML.Transition)) == 1

        # test preconditions
        assert t.subject == v1.subject.outgoing[0]
        assert t.subject == v2.subject.incoming[0]

        case.disconnect(t, t.tail)
        assert t.subject is None

        case.disconnect(t, t.head)
        assert t.subject is None

    def test_initial_pseudostate_connect(self, case):
        """Test transition and initial pseudostate connection."""
        v1 = case.create(PseudostateItem, UML.Pseudostate)
        v2 = case.create(StateItem, UML.State)

        t = case.create(TransitionItem)
        assert t.subject is None

        # connect head of transition to an initial pseudostate
        case.connect(t, t.head, v1)
        assert t.subject is None

        # connect tail of transition to a state
        case.connect(t, t.tail, v2)
        assert t.subject is not None

        assert len(case.kindof(UML.Transition)) == 1

        # test preconditions
        assert t.subject == v1.subject.outgoing[0]
        assert t.subject == v2.subject.incoming[0]

        # we should not be able to connect two transitions to initial
        # pseudostate
        t2 = case.create(TransitionItem)
        # connection to `t2` should not be possible as v1 is already connected
        # to `t`
        glued = case.allow(t2, t2.head, v1)
        assert not glued
        assert case.get_connected(t2.head) is None

    def test_initial_pseudostate_disconnect(self, case):
        """Test transition and initial pseudostate disconnection."""
        v1 = case.create(PseudostateItem, UML.Pseudostate)
        case.create(StateItem, UML.State)

        t = case.create(TransitionItem)
        assert t.subject is None

        # connect head of transition to an initial pseudostate
        case.connect(t, t.head, v1)
        assert case.get_connected(t.head)

        # perform the test
        case.disconnect(t, t.head)
        assert not case.get_connected(t.head)

    def test_initial_pseudostate_tail_glue(self, case):
        """Test transition tail and initial pseudostate gluing."""

        v1 = case.create(PseudostateItem, UML.Pseudostate)
        t = case.create(TransitionItem)
        assert t.subject is None

        # no tail connection should be possible
        glued = case.allow(t, t.tail, v1)
        assert not glued

    def test_final_state_connect(self, case):
        """Test transition to final state connection."""
        v1 = case.create(StateItem, UML.State)
        v2 = case.create(FinalStateItem, UML.FinalState)
        t = case.create(TransitionItem)

        # connect head of transition to a state
        case.connect(t, t.head, v1)

        # check if transition can connect to final state
        glued = case.allow(t, t.tail, v2)
        assert glued
        # and connect tail of transition to final state
        case.connect(t, t.tail, v2)
        assert t.subject is not None

        assert len(case.kindof(UML.Transition)) == 1

        assert t.subject == v1.subject.outgoing[0]
        assert t.subject == v2.subject.incoming[0]
        assert t.subject.source == v1.subject
        assert t.subject.target == v2.subject

    def test_final_state_head_glue(self, case):
        """Test transition head to final state connection."""
        v = case.create(FinalStateItem, UML.FinalState)
        t = case.create(TransitionItem)

        glued = case.allow(t, t.head, v)
        assert not glued
