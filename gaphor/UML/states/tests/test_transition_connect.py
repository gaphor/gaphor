"""Test transition item and state vertices connections."""

import pytest

from gaphor import UML
from gaphor.diagram.tests.fixtures import allow, connect, disconnect, get_connected
from gaphor.UML.states.finalstate import FinalStateItem
from gaphor.UML.states.pseudostates import PseudostateItem
from gaphor.UML.states.state import StateItem
from gaphor.UML.states.transition import TransitionItem


@pytest.fixture
def select(element_factory):
    return element_factory.lselect


def test_vertex_connect(create, select):
    v1 = create(StateItem, UML.State)
    v2 = create(StateItem, UML.State)

    t = create(TransitionItem)

    # connect vertices with transition
    connect(t, t.head, v1)
    connect(t, t.tail, v2)

    assert t.subject is not None

    assert len(select(UML.Transition)) == 1

    assert t.subject == v1.subject.outgoing[0]
    assert t.subject == v2.subject.incoming[0]
    assert t.subject.source == v1.subject
    assert t.subject.target == v2.subject


def test_vertex_reconnect(create, select, sanitizer_service):
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
    assert len(select(UML.Transition)) == 1

    assert t.subject == v1.subject.outgoing[0]
    assert t.subject == v3.subject.incoming[0]
    assert t.subject.source == v1.subject
    assert t.subject.target == v3.subject

    assert len(v2.subject.incoming) == 0
    assert len(v2.subject.outgoing) == 0


def test_vertex_disconnect(create, select):
    t = create(TransitionItem)
    v1 = create(StateItem, UML.State)
    v2 = create(StateItem, UML.State)

    connect(t, t.head, v1)
    connect(t, t.tail, v2)
    assert t.subject is not None

    assert len(select(UML.Transition)) == 1

    # test preconditions
    assert t.subject == v1.subject.outgoing[0]
    assert t.subject == v2.subject.incoming[0]

    disconnect(t, t.tail)
    assert t.subject is None

    disconnect(t, t.head)
    assert t.subject is None


def test_state_connect_to_same_item(create):
    """Test transition to state vertex connection."""
    v1 = create(StateItem, UML.State)
    t = create(TransitionItem)

    connect(t, t.head, v1)

    assert allow(t, t.tail, v1)


def test_initial_pseudostate_connect(create, select):
    v1 = create(PseudostateItem, UML.Pseudostate)
    v2 = create(StateItem, UML.State)

    t = create(TransitionItem)

    # connect head of transition to an initial pseudostate
    connect(t, t.head, v1)
    assert t.subject is None

    # connect tail of transition to a state
    connect(t, t.tail, v2)
    assert t.subject is not None

    assert len(select(UML.Transition)) == 1
    assert t.subject == v1.subject.outgoing[0]
    assert t.subject == v2.subject.incoming[0]


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


def test_final_state_connect(create, select):
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

    assert len(select(UML.Transition)) == 1

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
