from gaphas.guide import GuidedItemMoveMixin
from gaphas.move import ItemMove
from gaphas.move import Move as MoveAspect

from gaphor.diagram.group import group, ungroup
from gaphor.diagram.tools.dropzone import DropZoneMoveMixin, grow_parent
from gaphor.UML.states.pseudostates import PseudostateItem
from gaphor.UML.states.state import StateItem
from gaphor.UML.states.statemachine import StateMachineItem
from gaphor.UML.states.transition import TransitionItem


class RegionDropZoneMoveMixin(DropZoneMoveMixin):
    """This drop zone aspect has some specifics to drop a state in the right
    region on a state (machine)."""

    def stop_move(self, pos):
        view = self.view
        new_parent = view.selection.dropzone_item
        if (
            not isinstance(new_parent, (StateItem, StateMachineItem))
            or not new_parent.subject
            or not new_parent.subject.region
        ):
            return super().stop_move(pos)

        item = self.item
        old_parent = item.parent

        if not item.subject:
            GuidedItemMoveMixin.stop_move(self, pos)
            return

        item_pos = view.get_matrix_v2i(new_parent).transform_point(*pos)
        target_subject = new_parent.subject_at_point(item_pos)

        if target_subject is item.subject.container:
            GuidedItemMoveMixin.stop_move(self, pos)
            return

        if old_parent and ungroup(old_parent.subject, item.subject):
            item.change_parent(None)
            old_parent.request_update()

        item_pos = view.get_matrix_v2i(new_parent).transform_point(*pos)
        target_subject = new_parent.subject_at_point(item_pos)
        if group(target_subject, item.subject):
            grow_parent(new_parent, item)
            item.change_parent(new_parent)

        GuidedItemMoveMixin.stop_move(self, pos)


@MoveAspect.register(StateItem)
@MoveAspect.register(PseudostateItem)
@MoveAspect.register(TransitionItem)
class DropZoneMove(RegionDropZoneMoveMixin, GuidedItemMoveMixin, ItemMove):
    pass
