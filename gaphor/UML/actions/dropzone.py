from gaphas.guide import GuidedItemMoveMixin
from gaphas.move import ItemMove
from gaphas.move import Move as MoveAspect

from gaphor.diagram.drop import grow_parent
from gaphor.diagram.group import group, ungroup
from gaphor.diagram.tools.dropzone import DropZoneMoveMixin
from gaphor.UML.actions.action import (
    AcceptEventActionItem,
    ActionItem,
    CallBehaviorActionItem,
    SendSignalActionItem,
    ValueSpecificationActionItem,
)
from gaphor.UML.actions.objectnode import ObjectNodeItem
from gaphor.UML.actions.partition import PartitionItem


class PartitionDropZoneMoveMixin(DropZoneMoveMixin):
    """This drop zone aspect has some specifics to drop a state in the right
    partition (swim lane)."""

    def drop(self, new_parent, pos):
        view = self.view

        if not isinstance(new_parent, PartitionItem) or not new_parent.subject:
            return super().drop(new_parent, pos)

        item = self.item
        old_parent = item.parent

        if not item.subject:
            return

        item_pos = view.get_matrix_v2i(new_parent).transform_point(*pos)
        target_subject = new_parent.partition_at_point(item_pos)

        if target_subject is item.subject.inPartition:
            return

        if old_parent and any(ungroup(p, item.subject) for p in old_parent.partition):
            item.change_parent(None)
            old_parent.request_update()

        if group(target_subject, item.subject):
            grow_parent(new_parent, item)
            item.change_parent(new_parent)


@MoveAspect.register(ActionItem)
@MoveAspect.register(AcceptEventActionItem)
@MoveAspect.register(SendSignalActionItem)
@MoveAspect.register(CallBehaviorActionItem)
@MoveAspect.register(ValueSpecificationActionItem)
@MoveAspect.register(ObjectNodeItem)
class DropZoneMove(PartitionDropZoneMoveMixin, GuidedItemMoveMixin, ItemMove):
    pass
