from gaphor.core.modeling import Diagram
from gaphor.diagram.drop import drop, grow_parent
from gaphor.diagram.group import group, ungroup
from gaphor.diagram.presentation import connect
from gaphor.diagram.support import get_diagram_item
from gaphor.UML.actions.action import (
    AcceptEventActionItem,
    ActionItem,
    CallBehaviorActionItem,
    SendSignalActionItem,
    ValueSpecificationActionItem,
)
from gaphor.UML.actions.objectnode import ObjectNodeItem
from gaphor.UML.actions.partition import PartitionItem
from gaphor.UML.uml import ActivityParameterNode


@drop.register(ActivityParameterNode, Diagram)
def drop_relationship(element: ActivityParameterNode, diagram: Diagram, x, y):
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


@drop.register(ActionItem, PartitionItem)
@drop.register(AcceptEventActionItem, PartitionItem)
@drop.register(SendSignalActionItem, PartitionItem)
@drop.register(CallBehaviorActionItem, PartitionItem)
@drop.register(ValueSpecificationActionItem, PartitionItem)
@drop.register(ObjectNodeItem, PartitionItem)
def drop_on_partition(item, new_parent, x, y):
    assert item.diagram is new_parent.diagram

    if not item.subject:
        return

    old_parent = item.parent
    target_subject = new_parent.partition_at_point((x, y))

    if target_subject is item.subject.inPartition:
        return

    if old_parent and any(ungroup(p, item.subject) for p in old_parent.partition):
        item.change_parent(None)
        old_parent.request_update()

    if group(target_subject, item.subject):
        grow_parent(new_parent, item)
        item.change_parent(new_parent)
