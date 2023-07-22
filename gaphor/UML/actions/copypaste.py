from gaphor.diagram.copypaste import copy, copy_presentation
from gaphor.UML import Activity, ActivityParameterNode
from gaphor.UML.actions.activity import ActivityParameterNodeItem
from gaphor.UML.actions.partition import PartitionItem
from gaphor.UML.copypaste import copy_named_element


@copy.register
def copy_partition_item(element: PartitionItem):
    yield element.id, copy_presentation(element)
    for partition in element.partition:
        yield from copy(partition)


@copy.register
def copy_activity(element: Activity):
    yield element.id, copy_named_element(element)
    for node in element.node:
        if isinstance(node, ActivityParameterNode):
            yield from copy(node)


@copy.register
def copy_activity_parameter_node(element: ActivityParameterNode):
    yield element.id, copy_named_element(element)
    yield from copy(element.parameter)


@copy.register
def copy_activity_parameter_node_item(element: ActivityParameterNodeItem):
    return []
