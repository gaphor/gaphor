from gaphor import UML
from gaphor.diagram.group import group, ungroup


def test_state_in_state_machine(element_factory):
    s = element_factory.create(UML.State)
    sm = element_factory.create(UML.StateMachine)

    group(sm, s)

    assert s.container in sm.region


def test_pseudostate_in_state_machine(element_factory):
    s = element_factory.create(UML.Pseudostate)
    sm = element_factory.create(UML.StateMachine)

    group(sm, s)

    assert s.container in sm.region


def test_state_in_region(element_factory):
    s = element_factory.create(UML.State)
    region = element_factory.create(UML.Region)

    group(region, s)

    assert s.container is region
    assert s in region.subvertex


def test_state_in_state(element_factory):
    s = element_factory.create(UML.State)
    parent = element_factory.create(UML.State)

    group(parent, s)

    assert s.container in parent.region


def test_ungroup_state_in_state_machine(element_factory):
    s = element_factory.create(UML.State)
    sm = element_factory.create(UML.StateMachine)

    group(sm, s)
    ungroup(sm, s)

    assert not s.container
    assert sm.region


def test_ungroup_pseudostate_in_state_machine(element_factory):
    s = element_factory.create(UML.Pseudostate)
    sm = element_factory.create(UML.StateMachine)

    group(sm, s)
    ungroup(sm, s)

    assert not s.container
    assert sm.region


def test_ungroup_state_in_region(element_factory):
    s = element_factory.create(UML.State)
    region = element_factory.create(UML.Region)

    group(region, s)
    ungroup(region, s)

    assert not s.container


def test_ungroup_state_in_state(element_factory):
    s = element_factory.create(UML.State)
    parent = element_factory.create(UML.State)

    group(parent, s)
    ungroup(parent, s)

    assert not s.container
    assert parent.region
