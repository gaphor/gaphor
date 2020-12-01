from gaphor.diagram.grouping import AbstractGroup, Group
from gaphor.UML.actions.action import ActionItem
from gaphor.UML.actions.activitynodes import ActivityNodeItem, ForkNodeItem
from gaphor.UML.actions.objectnode import ObjectNodeItem
from gaphor.UML.actions.partition import PartitionItem


class ActivityNodePartitionGroup(AbstractGroup):
    """Group activity nodes within activity partition."""

    def can_contain(self):
        return self.parent.subject and len(self.parent.subject.subpartition) == 0

    def group(self):
        partition = self.parent.subject
        node = self.item.subject
        partition.node = node

    def ungroup(self):
        partition = self.parent.subject
        node = self.item.subject
        partition.node.remove(node)


Group.register(PartitionItem, ActivityNodeItem)(ActivityNodePartitionGroup)
Group.register(PartitionItem, ActionItem)(ActivityNodePartitionGroup)
Group.register(PartitionItem, ObjectNodeItem)(ActivityNodePartitionGroup)
Group.register(PartitionItem, ForkNodeItem)(ActivityNodePartitionGroup)
