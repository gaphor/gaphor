"""Tests for grouping functionality in Gaphor."""

from gaphor import UML
from gaphor.UML.actions import ActionItem, PartitionItem


class TestPartitionGroup:
    def test_no_subpartition_when_nodes_in(self, case):
        """Test adding subpartition when nodes added."""
        p = case.create(PartitionItem, subject_cls=UML.ActivityPartition)
        a1 = case.create(ActionItem, UML.Action)
        p1 = case.create(PartitionItem, subject_cls=UML.ActivityPartition)
        p2 = case.create(PartitionItem, subject_cls=UML.ActivityPartition)

        case.group(p, p1)
        case.group(p1, a1)
        assert not case.can_group(p1, p2)

    def test_action_grouping(self, case):
        """Test adding action to partition."""
        p1 = case.create(PartitionItem, subject_cls=UML.ActivityPartition)
        p2 = case.create(PartitionItem, subject_cls=UML.ActivityPartition)
        a1 = case.create(ActionItem, UML.Action)
        a2 = case.create(ActionItem, UML.Action)

        assert case.can_group(p1, a1)
        case.group(p1, a1)
        assert len(p1.subject.node) == 1

        case.group(p1, p2)
        case.group(p2, a1)

        assert case.can_group(p2, a1)
        assert len(p2.subject.node) == 1
        case.group(p2, a2)
        assert len(p2.subject.node) == 2

    def test_ungrouping(self, case):
        """Test action and partition removal."""
        p = case.create(PartitionItem, subject_cls=UML.ActivityPartition)
        a1 = case.create(ActionItem, UML.Action)
        a2 = case.create(ActionItem, UML.Action)

        case.group(p, a1)
        case.group(p, a2)

        case.ungroup(p, a1)
        assert len(p.subject.node) == 1
        case.ungroup(p, a2)
        assert len(p.subject.node) == 0

    def test_ungrouping_with_actions(self, case):
        """Test partition with actions removal."""
        p = case.create(PartitionItem, subject_cls=UML.ActivityPartition)
        a1 = case.create(ActionItem, UML.Action)
        a2 = case.create(ActionItem, UML.Action)

        case.group(p, a1)
        case.group(p, a2)

        partition = p.subject
        assert len(partition.node) == 2, partition.node
        assert len(p.children) == 2, p.children

        case.ungroup(p, a1)
        case.ungroup(p, a2)

        assert 0 == len(partition.node)
        assert len(p.children) == 0
        assert len(partition.node) == 0
