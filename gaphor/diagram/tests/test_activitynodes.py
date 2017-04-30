from __future__ import absolute_import
from gaphor.UML import uml2
from gaphor.diagram import items
from gaphor.tests.testcase import TestCase

class ActivityNodesTestCase(TestCase):

    def test_decision_node(self):
        """Test creation of decision node
        """
        self.create(items.DecisionNodeItem, uml2.DecisionNode)


    def test_fork_node(self):
        """Test creation of fork node
        """
        self.create(items.ForkNodeItem, uml2.ForkNode)


    def test_decision_node_persistence(self):
        """Test saving/loading of decision node
        """
        factory = self.element_factory
        item = self.create(items.DecisionNodeItem, uml2.DecisionNode)

        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, items.DecisionNodeItem))[0]
        self.assertTrue(item.combined is None, item.combined)

        merge_node = factory.create(uml2.MergeNode)
        item.combined = merge_node
        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, items.DecisionNodeItem))[0]
        self.assertTrue(item.combined is not None, item.combined)
        self.assertTrue(isinstance(item.combined, uml2.MergeNode))


    def test_fork_node_persistence(self):
        """Test saving/loading of fork node
        """
        factory = self.element_factory
        item = self.create(items.ForkNodeItem, uml2.ForkNode)

        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, items.ForkNodeItem))[0]
        self.assertTrue(item.combined is None, item.combined)

        merge_node = factory.create(uml2.JoinNode)
        item.combined = merge_node
        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, items.ForkNodeItem))[0]
        self.assertTrue(item.combined is not None, item.combined)
        self.assertTrue(isinstance(item.combined, uml2.JoinNode))


# vim:sw=4:et:ai
