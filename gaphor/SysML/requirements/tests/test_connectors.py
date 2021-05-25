import pytest

from gaphor import UML
from gaphor.diagram.tests.fixtures import allow, connect, disconnect
from gaphor.SysML import sysml
from gaphor.SysML.requirements.relationships import (
    DeriveReqtItem,
    RefineItem,
    SatisfyItem,
    TraceItem,
    VerifyItem,
)
from gaphor.SysML.requirements.requirement import RequirementItem
from gaphor.UML.classes import ContainmentItem


@pytest.mark.parametrize(
    "item_class", [DeriveReqtItem, RefineItem, SatisfyItem, TraceItem, VerifyItem]
)
def test_relation_allow_connect_disconnect_cycle(create, diagram, item_class):
    req1 = create(RequirementItem, sysml.Requirement)
    req2 = create(RequirementItem, sysml.Requirement)

    relation = diagram.create(item_class)

    assert allow(relation, relation.handles()[0], req1)
    assert allow(relation, relation.handles()[1], req2)

    connect(relation, relation.handles()[0], req1)
    connect(relation, relation.handles()[1], req2)

    assert relation.subject
    assert relation.subject.sourceContext is req1.subject
    assert relation.subject.targetContext is req2.subject

    disconnect(relation, relation.handles()[0])

    assert not relation.subject


def test_containment_between_requirements(create, diagram):
    """Test containment connecting between two requirements."""
    container_req = create(RequirementItem, sysml.Requirement)
    contained_req = create(RequirementItem, sysml.Requirement)
    line = create(ContainmentItem)

    connect(line, line.head, container_req)
    connect(line, line.tail, contained_req)

    assert diagram.connections.get_connection(line.tail).connected is contained_req
    assert len(container_req.subject.ownedElement) == 1
    assert contained_req.subject in container_req.subject.ownedElement


def test_containment_container_req_class_disconnect(create, diagram, element_factory):
    """Test containment disconnecting from two requirements."""
    parent_package = element_factory.create(UML.Package)
    diagram.element = parent_package
    container_req = create(RequirementItem, sysml.Requirement)
    contained_req = create(RequirementItem, sysml.Requirement)
    line = create(ContainmentItem)

    connect(line, line.tail, contained_req)
    connect(line, line.head, container_req)
    assert contained_req.subject not in parent_package.ownedElement

    disconnect(line, line.head)
    assert contained_req.subject in parent_package.ownedElement
