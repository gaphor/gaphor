from gaphas.guide import GuidedItemMoveMixin
from gaphas.move import ItemMove
from gaphas.move import Move as MoveAspect

from gaphor.diagram.group import group, ungroup
from gaphor.diagram.tools.dropzone import DropZoneMoveMixin, grow_parent
from gaphor.UML.states.state import StateItem
from gaphor.UML.states.statemachine import StateMachineItem


class RegionDropZoneMoveMixin(DropZoneMoveMixin):
    """This drop zone aspect has some specifics to drop a state in the right
    region on a state (machine)."""

    def stop_move(self, pos):
        view = self.view
        new_parent = view.selection.dropzone_item
        if (
            not isinstance(new_parent, StateMachineItem)
            or not new_parent.subject
            or not new_parent.subject.region
        ):
            return super().stop_move(pos)

        item = self.item
        old_parent = item.parent

        try:
            if not item.subject:
                return

            item_pos = view.get_matrix_v2i(new_parent).transform_point(*pos)
            target_subject = new_parent.subject_at_point(item_pos)

            if target_subject is item.subject.container:
                return

            if old_parent and ungroup(old_parent.subject, item.subject):
                item.change_parent(None)
                old_parent.request_update()

            item_pos = view.get_matrix_v2i(new_parent).transform_point(*pos)
            target_subject = new_parent.subject_at_point(item_pos)
            if group(target_subject, item.subject):
                grow_parent(new_parent, item)
                item.change_parent(new_parent)
        finally:
            view.selection.dropzone_item = None


@MoveAspect.register(StateItem)
class DropZoneMove(RegionDropZoneMoveMixin, GuidedItemMoveMixin, ItemMove):
    pass
