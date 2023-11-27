import pytest

from gaphor.diagram.tests.fixtures import allow, connect, disconnect
from gaphor.SysML.allocations.relationships import AllocateItem
from gaphor.SysML.blocks.block import BlockItem
from gaphor.SysML.blocks.interfaceblock import InterfaceBlockItem
from gaphor.SysML.sysml import Block, InterfaceBlock
from gaphor.UML.actions.activity import ActivityItem
from gaphor.UML.interactions.interaction import InteractionItem
from gaphor.UML.states.statemachine import StateMachineItem
from gaphor.UML.uml import Activity, Interaction, StateMachine

# Some selection of items
items = [
    (Block, BlockItem),
    (InterfaceBlock, InterfaceBlockItem),
    (Activity, ActivityItem),
    (Interaction, InteractionItem),
    (StateMachine, StateMachineItem),
]


@pytest.mark.parametrize("source_types", items)
@pytest.mark.parametrize("target_types", items)
def test_allocate_relationship(create, diagram, source_types, target_types):
    source = create(source_types[1], source_types[0])
    target = create(target_types[1], target_types[0])

    allocate = diagram.create(AllocateItem)

    assert allow(allocate, allocate.handles()[0], source)
    assert allow(allocate, allocate.handles()[1], target)

    connect(allocate, allocate.handles()[0], source)
    connect(allocate, allocate.handles()[1], target)

    assert allocate.subject
    assert allocate.subject.sourceContext is source.subject
    assert allocate.subject.targetContext is target.subject

    disconnect(allocate, allocate.handles()[0])

    assert not allocate.subject
