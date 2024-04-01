from gaphas.guide import GuidedItemMoveMixin
from gaphas.move import ItemMove
from gaphas.move import Move as MoveAspect

from gaphor.diagram.drop import grow_parent
from gaphor.diagram.group import group, ungroup
from gaphor.diagram.tools.dropzone import DropZoneMoveMixin
from gaphor.UML.states.pseudostates import PseudostateItem
from gaphor.UML.states.state import StateItem
from gaphor.UML.states.statemachine import StateMachineItem
from gaphor.UML.states.transition import TransitionItem


class RegionDropZoneMoveMixin(DropZoneMoveMixin):
    """This drop zone aspect has some specifics to drop a state in the right
    region on a state (machine)."""

    def drop(self, new_parent, pos):
        view = self.view

        if (
            not isinstance(new_parent, (StateItem, StateMachineItem))
            or not new_parent.subject
            or not new_parent.subject.region
        ):
            return super().drop(new_parent, pos)

        item = self.item
        old_parent = item.parent

        if not item.subject:
            return

        item_pos = view.get_matrix_v2i(new_parent).transform_point(*pos)
        target_subject = new_parent.region_at_point(item_pos)

        if target_subject is item.subject.container:
            return

        if old_parent and ungroup(old_parent.subject, item.subject):
            item.change_parent(None)
            old_parent.request_update()

        if group(target_subject, item.subject):
            grow_parent(new_parent, item)
            item.change_parent(new_parent)


@MoveAspect.register(StateItem)
@MoveAspect.register(PseudostateItem)
@MoveAspect.register(TransitionItem)
class DropZoneMove(RegionDropZoneMoveMixin, GuidedItemMoveMixin, ItemMove):
    pass
