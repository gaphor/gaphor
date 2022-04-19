"""Tests for grouping functionality in Gaphor."""

from gaphor import UML
from gaphor.diagram.group import group, ungroup
from gaphor.UML.actions import ActionItem, PartitionItem


def test_add_node_to_activity(element_factory):
    node = element_factory.create(UML.Action)
    activity = element_factory.create(UML.Activity)

    assert group(activity, node)
    assert node in activity.node
    assert node.owner is activity


def test_ungroup_node_to_activity(element_factory):
    node = element_factory.create(UML.Action)
    activity = element_factory.create(UML.Activity)

    assert group(activity, node)
    assert ungroup(activity, node)
    assert node not in activity.node
    assert not node.owner


def test_no_subpartition_when_nodes_in(element_factory):
    """Test adding subpartition when nodes added."""
    p = element_factory.create(UML.ActivityPartition)
    a1 = element_factory.create(UML.Action)
    p1 = element_factory.create(UML.ActivityPartition)
    p2 = element_factory.create(UML.ActivityPartition)

    group(p, p1)
    group(p1, a1)
    assert not group(p1, p2)


def test_action_grouping(element_factory):
    """Test adding action to partition."""
    p1 = element_factory.create(UML.ActivityPartition)
    p2 = element_factory.create(UML.ActivityPartition)
    a1 = element_factory.create(UML.Action)
    a2 = element_factory.create(UML.Action)

    group(p1, a1)
    assert len(p1.node) == 1

    group(p1, p2)
    group(p2, a1)

    assert len(p2.node) == 1
    group(p2, a2)
    assert len(p2.node) == 2


def test_ungrouping(element_factory):
    """Test action and partition removal."""
    p = element_factory.create(UML.ActivityPartition)
    a1 = element_factory.create(UML.Action)
    a2 = element_factory.create(UML.Action)

    group(p, a1)
    group(p, a2)

    ungroup(p, a1)
    assert len(p.node) == 1
    ungroup(p, a2)
    assert len(p.node) == 0


def test_ungrouping_with_actions(create):
    """Test partition with actions removal."""
    p = create(PartitionItem, UML.ActivityPartition)
    a1 = create(ActionItem, UML.Action)
    a2 = create(ActionItem, UML.Action)
    partition = p.subject

    group(partition, a1.subject)
    group(partition, a2.subject)

    assert len(partition.node) == 2, partition.node

    ungroup(p.subject, a1.subject)
    ungroup(p.subject, a2.subject)

    assert len(p.children) == 0
    assert len(partition.node) == 0
