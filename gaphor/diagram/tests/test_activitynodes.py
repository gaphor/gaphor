import gaphor.UML as UML
from gaphor.diagram import items
from gaphor.tests.testcase import TestCase

class ActivityNodesTestCase(TestCase):
    def test_decision_node(self):
        self.create(items.DecisionNodeItem, UML.DecisionNode)

    def test_fork_node(self):
        self.create(items.ForkNodeItem, UML.ForkNode)

# vim:sw=4:et:ai
