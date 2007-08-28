import unittest
import gaphor.UML as UML
from gaphor.diagram import items
from gaphor.application import Application

class ActivityNodesTestCase(unittest.TestCase):

    def setUp(self):
        Application.init(services=['element_factory'])
        self.element_factory = Application.get_service('element_factory')
        self.diagram = self.element_factory.create(UML.Diagram)

    def shutDown(self):
        Application.shutdown()

    def test_decision_node(self):
        return self.diagram.create(items.DecisionNodeItem, subject=self.element_factory.create(UML.DecisionNode))

    def test_fork_node(self):
        return self.diagram.create(items.ForkNodeItem, subject=self.element_factory.create(UML.ForkNode))

# vim:sw=4:et:ai
