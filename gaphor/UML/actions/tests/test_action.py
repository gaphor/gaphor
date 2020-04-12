"""
Test actions.
"""

from gaphor import UML
from gaphor.tests.testcase import TestCase
from gaphor.UML.actions.action import ActionItem


class ActionTestCase(TestCase):
    def test_action(self):
        """Test creation of actions.
        """
        self.create(ActionItem, UML.Action)
