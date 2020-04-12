import gaphor.UML as UML
from gaphor.tests.testcase import TestCase
from gaphor.UML.actions.activitynodes import DecisionNodeItem, ForkNodeItem


class ActivityNodesTestCase(TestCase):
    def test_decision_node(self):
        """Test creation of decision node
        """
        self.create(DecisionNodeItem, UML.DecisionNode)

    def test_fork_node(self):
        """Test creation of fork node
        """
        self.create(ForkNodeItem, UML.ForkNode)

    def test_decision_node_persistence(self):
        """Test saving/loading of decision node
        """
        factory = self.element_factory
        item = self.create(DecisionNodeItem, UML.DecisionNode)

        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, DecisionNodeItem))[0]
        assert item.combined is None, item.combined

        merge_node = factory.create(UML.MergeNode)
        item.combined = merge_node
        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, DecisionNodeItem))[0]
        assert item.combined is not None, item.combined
        assert isinstance(item.combined, UML.MergeNode)

    def test_fork_node_persistence(self):
        """Test saving/loading of fork node
        """
        factory = self.element_factory
        item = self.create(ForkNodeItem, UML.ForkNode)

        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, ForkNodeItem))[0]
        assert item.combined is None, item.combined

        merge_node = factory.create(UML.JoinNode)
        item.combined = merge_node
        data = self.save()
        self.load(data)

        item = self.diagram.canvas.select(lambda e: isinstance(e, ForkNodeItem))[0]
        assert item.combined is not None, item.combined
        assert isinstance(item.combined, UML.JoinNode)
