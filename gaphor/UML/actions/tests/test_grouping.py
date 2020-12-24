"""Tests for grouping functionality in Gaphor."""

from gaphor import UML
from gaphor.tests import TestCase
from gaphor.UML.actions import ActionItem, PartitionItem


class PartitionGroupTestCase(TestCase):
    def test_no_subpartition_when_nodes_in(self):
        """Test adding subpartition when nodes added."""
        p = self.create(PartitionItem, subject_cls=UML.ActivityPartition)
        a1 = self.create(ActionItem, UML.Action)
        p1 = self.create(PartitionItem, subject_cls=UML.ActivityPartition)
        p2 = self.create(PartitionItem, subject_cls=UML.ActivityPartition)

        self.group(p, p1)
        self.group(p1, a1)
        assert not self.can_group(p1, p2)

    def test_action_grouping(self):
        """Test adding action to partition."""
        p1 = self.create(PartitionItem, subject_cls=UML.ActivityPartition)
        p2 = self.create(PartitionItem, subject_cls=UML.ActivityPartition)
        a1 = self.create(ActionItem, UML.Action)
        a2 = self.create(ActionItem, UML.Action)

        assert self.can_group(p1, a1)
        self.group(p1, a1)
        assert len(p1.subject.node) == 1

        self.group(p1, p2)
        self.group(p2, a1)

        assert self.can_group(p2, a1)
        assert len(p2.subject.node) == 1
        self.group(p2, a2)
        assert len(p2.subject.node) == 2

    def test_ungrouping(self):
        """Test action and partition removal."""
        p = self.create(PartitionItem, subject_cls=UML.ActivityPartition)
        a1 = self.create(ActionItem, UML.Action)
        a2 = self.create(ActionItem, UML.Action)

        self.group(p, a1)
        self.group(p, a2)

        self.ungroup(p, a1)
        assert len(p.subject.node) == 1
        self.ungroup(p, a2)
        assert len(p.subject.node) == 0

    def test_ungrouping_with_actions(self):
        """Test partition with actions removal."""
        p = self.create(PartitionItem, subject_cls=UML.ActivityPartition)
        a1 = self.create(ActionItem, UML.Action)
        a2 = self.create(ActionItem, UML.Action)

        self.group(p, a1)
        self.group(p, a2)

        partition = p.subject
        assert len(partition.node) == 2, partition.node
        assert len(p.children) == 2, p.children

        self.ungroup(p, a1)
        self.ungroup(p, a2)

        assert 0 == len(partition.node)
        assert len(p.children) == 0
        assert len(partition.node) == 0
