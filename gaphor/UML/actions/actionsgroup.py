from gaphor.diagram.group import group, ungroup
from gaphor.UML.uml import ActivityNode, ActivityPartition


@group.register(ActivityPartition, ActivityNode)
def activity_node_partition_group(partition, node):
    """Group activity nodes within activity partition."""
    if partition.subpartition:
        return False
    partition.node = node
    return True


@ungroup.register(ActivityPartition, ActivityNode)
def activity_node_group(partition, node):
    if node in partition.node:
        partition.node.remove(node)
        return True
    return False
