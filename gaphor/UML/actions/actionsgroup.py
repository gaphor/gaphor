from gaphor.diagram.group import group
from gaphor.UML.uml import ActivityNode, ActivityPartition


@group.register(ActivityPartition, ActivityNode)
def activity_node_partition_group(partition, node):
    """Group activity nodes within activity partition."""
    partition.node = node
    return True
