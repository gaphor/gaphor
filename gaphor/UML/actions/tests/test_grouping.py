"""Tests for grouping functionality in Gaphor."""

from gaphor import UML
from gaphor.diagram.group import group, ungroup
from gaphor.UML.actions import ActionItem, PartitionItem


def test_no_subpartition_when_nodes_in(case):
    """Test adding subpartition when nodes added."""
    p = case.create(PartitionItem, subject_cls=UML.ActivityPartition)
    a1 = case.create(ActionItem, UML.Action)
    p1 = case.create(PartitionItem, subject_cls=UML.ActivityPartition)
    p2 = case.create(PartitionItem, subject_cls=UML.ActivityPartition)

    group(p, p1)
    group(p1, a1)
    assert not group(p1, p2)


def test_action_grouping(case):
    """Test adding action to partition."""
    p1 = case.create(PartitionItem, subject_cls=UML.ActivityPartition)
    p2 = case.create(PartitionItem, subject_cls=UML.ActivityPartition)
    a1 = case.create(ActionItem, UML.Action)
    a2 = case.create(ActionItem, UML.Action)

    group(p1.subject, a1.subject)
    assert len(p1.subject.node) == 1

    group(p1.subject, p2.subject)
    group(p2.subject, a1.subject)

    assert len(p2.subject.node) == 1
    group(p2.subject, a2.subject)
    assert len(p2.subject.node) == 2


def test_ungrouping(case):
    """Test action and partition removal."""
    p = case.create(PartitionItem, subject_cls=UML.ActivityPartition)
    a1 = case.create(ActionItem, UML.Action)
    a2 = case.create(ActionItem, UML.Action)

    group(p.subject, a1.subject)
    group(p.subject, a2.subject)

    ungroup(p.subject, a1.subject)
    assert len(p.subject.node) == 1
    ungroup(p.subject, a2.subject)
    assert len(p.subject.node) == 0


def test_ungrouping_with_actions(case):
    """Test partition with actions removal."""
    p = case.create(PartitionItem, subject_cls=UML.ActivityPartition)
    a1 = case.create(ActionItem, UML.Action)
    a2 = case.create(ActionItem, UML.Action)
    partition = p.subject

    group(partition, a1.subject)
    group(partition, a2.subject)

    assert len(partition.node) == 2, partition.node

    ungroup(p.subject, a1.subject)
    ungroup(p.subject, a2.subject)

    assert 0 == len(partition.node)
    assert len(p.children) == 0
    assert len(partition.node) == 0
