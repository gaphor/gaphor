"""Test actions."""

from gaphor import UML
from gaphor.UML.actions.action import ActionItem


def test_action(create):
    """Test creation of actions."""
    assert create(ActionItem, UML.Action)
