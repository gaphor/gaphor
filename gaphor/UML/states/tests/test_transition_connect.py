"""Test transition item and state vertices connections."""

from gaphor import UML
from gaphor.diagram.tests.fixtures import allow, connect, disconnect, get_connected
from gaphor.UML.states.finalstate import FinalStateItem
from gaphor.UML.states.pseudostates import PseudostateItem
from gaphor.UML.states.state import StateItem
from gaphor.UML.states.transition import TransitionItem


def test_vertex_connect(create, kindof):
    """Test transition to state vertex connection."""
    v1 = create(StateItem, UML.State)
    v2 = create(StateItem, UML.State)

    t = create(TransitionItem)
    assert t.subject is None

    # connect vertices with transition
    connect(t, t.head, v1)
    connect(t, t.tail, v2)

    assert t.subject is not None

    assert len(kindof(UML.Transition)) == 1

    assert t.subject == v1.subject.outgoing[0]
    assert t.subject == v2.subject.incoming[0]
    assert t.subject.source == v1.subject
    assert t.subject.target == v2.subject


def test_vertex_reconnect(create, kindof):
    """Test transition to state vertex reconnection."""
    v1 = create(StateItem, UML.State)
    v2 = create(StateItem, UML.State)
    v3 = create(StateItem, UML.State)

    t = create(TransitionItem)

    # connect: v1 -> v2
    connect(t, t.head, v1)
    connect(t, t.tail, v2)

    s = t.subject
    s.name = "tname"
    s.guard.specification = "tguard"

    # reconnect: v1 -> v3
    connect(t, t.tail, v3)

    assert s is not t.subject
    assert len(kindof(UML.Transition)) == 1

    assert t.subject == v1.subject.outgoing[0]
    assert t.subject == v3.subject.incoming[0]
    assert t.subject.source == v1.subject
    assert t.subject.target == v3.subject

    assert len(v2.subject.incoming) == 0
    assert len(v2.subject.outgoing) == 0


def test_vertex_disconnect(create, kindof):
    """Test transition and state vertices disconnection."""
    t = create(TransitionItem)
    v1 = create(StateItem, UML.State)
    v2 = create(StateItem, UML.State)

    connect(t, t.head, v1)
    connect(t, t.tail, v2)
    assert t.subject is not None

    assert len(kindof(UML.Transition)) == 1

    # test preconditions
    assert t.subject == v1.subject.outgoing[0]
    assert t.subject == v2.subject.incoming[0]

    disconnect(t, t.tail)
    assert t.subject is None

    disconnect(t, t.head)
    assert t.subject is None


def test_initial_pseudostate_connect(create, kindof):
    """Test transition and initial pseudostate connection."""
    v1 = create(PseudostateItem, UML.Pseudostate)
    v2 = create(StateItem, UML.State)

    t = create(TransitionItem)
    assert t.subject is None

    # connect head of transition to an initial pseudostate
    connect(t, t.head, v1)
    assert t.subject is None

    # connect tail of transition to a state
    connect(t, t.tail, v2)
    assert t.subject is not None

    assert len(kindof(UML.Transition)) == 1

    # test preconditions
    assert t.subject == v1.subject.outgoing[0]
    assert t.subject == v2.subject.incoming[0]

    # we should not be able to connect two transitions to initial
    # pseudostate
    t2 = create(TransitionItem)
    # connection to `t2` should not be possible as v1 is already connected
    # to `t`
    glued = allow(t2, t2.head, v1)
    assert not glued
    assert get_connected(t2, t2.head) is None


def test_initial_pseudostate_disconnect(create):
    """Test transition and initial pseudostate disconnection."""
    v1 = create(PseudostateItem, UML.Pseudostate)
    create(StateItem, UML.State)

    t = create(TransitionItem)
    assert t.subject is None

    # connect head of transition to an initial pseudostate
    connect(t, t.head, v1)
    assert get_connected(t, t.head)

    # perform the test
    disconnect(t, t.head)
    assert not get_connected(t, t.head)


def test_initial_pseudostate_tail_glue(create):
    """Test transition tail and initial pseudostate gluing."""

    v1 = create(PseudostateItem, UML.Pseudostate)
    t = create(TransitionItem)
    assert t.subject is None

    # no tail connection should be possible
    glued = allow(t, t.tail, v1)
    assert not glued


def test_final_state_connect(create, kindof):
    """Test transition to final state connection."""
    v1 = create(StateItem, UML.State)
    v2 = create(FinalStateItem, UML.FinalState)
    t = create(TransitionItem)

    # connect head of transition to a state
    connect(t, t.head, v1)

    # check if transition can connect to final state
    glued = allow(t, t.tail, v2)
    assert glued
    # and connect tail of transition to final state
    connect(t, t.tail, v2)
    assert t.subject is not None

    assert len(kindof(UML.Transition)) == 1

    assert t.subject == v1.subject.outgoing[0]
    assert t.subject == v2.subject.incoming[0]
    assert t.subject.source == v1.subject
    assert t.subject.target == v2.subject


def test_final_state_head_glue(create):
    """Test transition head to final state connection."""
    v = create(FinalStateItem, UML.FinalState)
    t = create(TransitionItem)

    glued = allow(t, t.head, v)
    assert not glued
