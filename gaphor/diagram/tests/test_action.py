"""
Test actions.
"""

import unittest

from gaphor import UML
from gaphor.diagram.action import ActionItem


class ActionTestCase(unittest.TestCase):

    def test_action(self):
        """Test creation of actions.
        """
        diagram = UML.create(UML.Diagram)
        klass = diagram.create(ActionItem, subject=UML.create(UML.Action))

        diagram.canvas.update()
