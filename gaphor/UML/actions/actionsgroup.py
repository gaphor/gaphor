from gaphor.diagram.group import group, ungroup
from gaphor.UML.uml import (
    Activity,
    ActivityNode,
    ActivityParameterNode,
    ActivityPartition,
)


@group.register(Activity, ActivityNode)
def activity_node_group(activity, node):
    activity.node = node
    return True


@ungroup.register(Activity, ActivityNode)
def activity_node_ungroup(activity, node):
    if node in activity.node:
        activity.node.remove(node)
        return True
    return False


@group.register(Activity, ActivityParameterNode)
def activity_parameter_node_group(activity, node):
    return False


@ungroup.register(Activity, ActivityParameterNode)
def activity_parameter_node_ungroup(activity, node):
    return False


@group.register(ActivityPartition, ActivityNode)
def activity_node_partition_group(partition, node):
    """Group activity nodes within activity partition."""
    if partition.subpartition:
        return False
    partition.node = node
    return True


@ungroup.register(ActivityPartition, ActivityNode)
def activity_node_partition_ungroup(partition, node):
    if node in partition.node:
        partition.node.remove(node)
        return True
    return False
