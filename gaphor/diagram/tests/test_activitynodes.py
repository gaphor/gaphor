import gaphor.UML as UML
from gaphor.diagram import items
from gaphor.tests.testcase import TestCase

class ActivityNodesTestCase(TestCase):

    def test_decision_node(self):
        """Test creation of decision node
        """
        self.create(items.DecisionNodeItem, UML.DecisionNode)


    def test_fork_node(self):
        """Test creation of fork node
        """
        self.create(items.ForkNodeItem, UML.ForkNode)


    def test_decision_node_persistence(self):
        """Test saving/loading of decision node
        """
        factory = self.element_factory
        item = self.create(items.DecisionNodeItem, UML.DecisionNode)

        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, items.DecisionNodeItem))[0]
        self.assertTrue(item.combined is None, item.combined)

        merge_node = factory.create(UML.MergeNode)
        item.combined = merge_node
        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, items.DecisionNodeItem))[0]
        self.assertTrue(item.combined is not None, item.combined)
        self.assertTrue(isinstance(item.combined, UML.MergeNode))


    def test_fork_node_persistence(self):
        """Test saving/loading of fork node
        """
        factory = self.element_factory
        item = self.create(items.ForkNodeItem, UML.ForkNode)

        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, items.ForkNodeItem))[0]
        self.assertTrue(item.combined is None, item.combined)

        merge_node = factory.create(UML.JoinNode)
        item.combined = merge_node
        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, items.ForkNodeItem))[0]
        self.assertTrue(item.combined is not None, item.combined)
        self.assertTrue(isinstance(item.combined, UML.JoinNode))


# vim:sw=4:et:ai
