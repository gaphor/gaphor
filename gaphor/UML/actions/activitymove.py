from gaphas.guide import GuidedItemHandleMoveMixin
from gaphas.handlemove import HandleMove, ItemHandleMove
from gaphas.move import Move
from gaphas.types import Pos

from gaphor.diagram.presentation import connect
from gaphor.diagram.tools.handlemove import GrayOutLineHandleMoveMixin
from gaphor.UML.actions.activity import ActivityParameterNodeItem


@HandleMove.register(ActivityParameterNodeItem)
class ActivityParameterNodeItemHandleMove(
    GrayOutLineHandleMoveMixin, GuidedItemHandleMoveMixin, ItemHandleMove
):
    """We use a custom tool for moving parameter nodes.

    Parameter nodes always connect to their parent (Activity).
    """

    def connect(self, pos: Pos) -> None:
        item = self.item
        connect(item, self.handle, item.parent)
        self.view.model.request_update(item)


@Move.register(ActivityParameterNodeItem)
def activity_parameter_node_move(item, view):
    """We use a custom tool for moving parameter nodes.

    They can be moved while handle is connected and will automatically
    connect to a side of its parent.
    """
    return ActivityParameterNodeItemHandleMove(item, item.handles()[0], view)
