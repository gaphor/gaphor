import pytest

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


@pytest.mark.parametrize(
    "item_class", [DeriveReqtItem, RefineItem, SatisfyItem, TraceItem, VerifyItem]
)
def test_relation_allow_connect_disconnect_cycle(diagram, element_factory, item_class):
    req1 = element_factory.create(sysml.Requirement)
    req2 = element_factory.create(sysml.Requirement)

    req_item1 = diagram.create(RequirementItem, subject=req1)
    req_item2 = diagram.create(RequirementItem, subject=req2)

    relation = diagram.create(item_class)

    assert allow(relation, relation.handles()[0], req_item1)
    assert allow(relation, relation.handles()[1], req_item2)

    connect(relation, relation.handles()[0], req_item1)
    connect(relation, relation.handles()[1], req_item2)

    assert relation.subject
    assert relation.subject.sourceContext is req_item1.subject
    assert relation.subject.targetContext is req_item2.subject

    disconnect(relation, relation.handles()[0])

    assert not relation.subject
