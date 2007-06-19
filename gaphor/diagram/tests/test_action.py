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
        element_factory = UML.ElementFactory()
        diagram = element_factory.create(UML.Diagram)
        klass = diagram.create(ActionItem, subject=element_factory.create(UML.Action))

        diagram.canvas.update()
