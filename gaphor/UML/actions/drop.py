from gaphor.core.modeling import Diagram
from gaphor.diagram.drop import (
    drop,
    drop_on_presentation,
    drop_relationship,
    grow_parent,
)
from gaphor.diagram.group import change_owner, ungroup
from gaphor.diagram.presentation import connect
from gaphor.diagram.support import get_diagram_item, get_diagram_item_metadata
from gaphor.UML.actions.action import (
    AcceptEventActionItem,
    ActionItem,
    CallBehaviorActionItem,
    SendSignalActionItem,
    ValueSpecificationActionItem,
)
from gaphor.UML.actions.objectnode import ObjectNodeItem
from gaphor.UML.actions.partition import PartitionItem
from gaphor.UML.drop import drop_relationship_on_diagram
from gaphor.UML.uml import ActivityEdge, ActivityParameterNode, ActivityPartition


@drop.register(ActivityEdge, Diagram)
def drop_activity_edge_on_diagram(element: ActivityEdge, diagram: Diagram, x, y):
    item_class = get_diagram_item(type(element))
    if not item_class:
        return None

    metadata = get_diagram_item_metadata(item_class)
    return (
        drop_relationship(
            element,
            metadata["head"].get(element),
            metadata["tail"].get(element),
            diagram,
            x,
            y,
        )
        if metadata
        else None
    )


@drop.register(ActivityParameterNode, Diagram)
def drop_parameter_node(element: ActivityParameterNode, diagram: Diagram, x, y):
    item_class = get_diagram_item(type(element))
    if not item_class:
        return None

    def drop_distance_to_item(item):
        local_x, local_y = item.matrix_i2c.inverse().transform_point(x, y)
        return item.point(local_x, local_y)

    appendable_item = min(
        diagram.select(
            lambda item: bool(element.activity and element.activity is item.subject)
        ),
        key=drop_distance_to_item,
        default=None,
    )

    if not appendable_item:
        return None

    item = diagram.create(item_class, subject=element)
    item.matrix.translate(x, y)
    item.change_parent(appendable_item)
    connect(item, item.handles()[0], appendable_item)

    return item


@drop.register(ActivityPartition, Diagram)
def drop_partition(partition: ActivityPartition, diagram: Diagram, x: float, y: float):
    item_class = get_diagram_item(type(partition))
    if not item_class:
        return None

    item = diagram.create(item_class)
    assert item

    item.matrix.translate(x, y)
    item.subject = partition
    item.partition = partition

    for node in partition.node:
        child_class = get_diagram_item(type(node))
        if not child_class:
            continue
        child_item = diagram.create(child_class)
        assert child_item
        child_item.subject = node
        child_item.diagram = diagram
        child_item.matrix.translate(x, y)
        drop_on_presentation(child_item, item, x, y)

    for node in partition.node:
        for outgoing in node.outgoing:
            if not outgoing.target:
                continue
            if partition.node.includes(outgoing.target):
                drop_relationship_on_diagram(outgoing, diagram, x, y)

    return item


@drop.register(ActionItem, PartitionItem)
@drop.register(AcceptEventActionItem, PartitionItem)
@drop.register(SendSignalActionItem, PartitionItem)
@drop.register(CallBehaviorActionItem, PartitionItem)
@drop.register(ValueSpecificationActionItem, PartitionItem)
@drop.register(ObjectNodeItem, PartitionItem)
def drop_on_partition(
    item: ActionItem
    | AcceptEventActionItem
    | SendSignalActionItem
    | CallBehaviorActionItem
    | ValueSpecificationActionItem
    | ObjectNodeItem,
    new_parent: PartitionItem,
    x: float,
    y: float,
):
    assert item.diagram is new_parent.diagram

    if not item.subject:
        return

    old_parent = item.parent
    target_subject = new_parent.partition_at_point((x, y))

    if target_subject is item.subject.inPartition:
        return

    if isinstance(old_parent, PartitionItem) and any(
        ungroup(p, item.subject) for p in old_parent.partition
    ):
        item.change_parent(None)
        old_parent.request_update()

    if change_owner(target_subject, item.subject):
        grow_parent(new_parent, item)
        item.change_parent(new_parent)
