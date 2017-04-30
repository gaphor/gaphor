"""
Test actions.
"""

from __future__ import absolute_import

from gaphor.UML import uml2
from gaphor.diagram.actions.action import ActionItem
from gaphor.tests.testcase import TestCase


class ActionTestCase(TestCase):
    def test_action(self):
        """Test creation of actions.
        """
        self.create(ActionItem, uml2.Action)
