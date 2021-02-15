"""Test actions."""

from gaphor import UML
from gaphor.UML.actions.action import ActionItem


def test_action(case):
    """Test creation of actions."""
    case.create(ActionItem, UML.Action)
