"""
Test actions.
"""

from gaphor import UML
from gaphor.diagram.action import ActionItem
from gaphor.tests.testcase import TestCase


class ActionTestCase(TestCase):
    def test_action(self):
        """Test creation of actions.
        """
        self.create(ActionItem, UML.Action)

