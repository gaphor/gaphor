from gaphor.diagram.copypaste import copy, copy_presentation
from gaphor.UML import (
    Activity,
    ActivityEdge,
    ActivityParameterNode,
    JoinNode,
    ObjectNode,
    Pin,
)
from gaphor.UML.actions.activity import ActivityParameterNodeItem
from gaphor.UML.actions.partition import PartitionItem
from gaphor.UML.copypaste import copy_multiplicity, copy_named_element


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


@copy.register
def copy_activity_edge(element: ActivityEdge):
    yield element.id, copy_named_element(element)
    if element.guard:
        yield from copy(element.guard)
    if element.weight:
        yield from copy(element.weight)


@copy.register
def copy_pin(element: Pin):
    yield element.id, copy_named_element(element)
    yield from copy_multiplicity(element)


@copy.register
def copy_object_node(element: ObjectNode):
    yield element.id, copy_named_element(element)
    if element.upperBound:
        yield from copy(element.upperBound)


@copy.register
def copy_join_node(element: JoinNode):
    yield element.id, copy_named_element(element)
    if element.joinSpec:
        yield from copy(element.joinSpec)
