"""Test actions."""

from gaphor import UML
from gaphor.UML.actions.action import ActionItem


def test_create_action(diagram, element_factory):
    action = element_factory.create(UML.Action)
    item = diagram.create(ActionItem, subject=action)

    assert item.subject is action
