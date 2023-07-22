"""Test call behaviour actions."""

from gaphor import UML
from gaphor.UML.actions.action import CallBehaviorActionItem


def test_create_callbehavioraction(diagram, element_factory):
    action = element_factory.create(UML.CallBehaviorAction)
    item = diagram.create(CallBehaviorActionItem, subject=action)

    assert item.subject is action


def test_load_action(element_factory, diagram, saver, loader):
    action = diagram.create(CallBehaviorActionItem)

    action.handles()[0].pos = (1, 2)
    action.matrix.translate(10, 20)
    action.width = 201
    action.height = 202

    dump = saver()
    loader(dump)

    new_action = next(element_factory.select(CallBehaviorActionItem))

    assert tuple(new_action.handles()[0].pos) == (1, 2)
    assert tuple(new_action.matrix) == (1.0, 0.0, 0.0, 1.0, 10, 20)
    assert new_action.width == 201
    assert new_action.height == 202
