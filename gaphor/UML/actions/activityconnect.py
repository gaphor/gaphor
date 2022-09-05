from gaphas.connector import Handle, Port
from gaphas.guide import GuidedItemHandleMoveMixin
from gaphas.handlemove import HandleMove, ItemHandleMove
from gaphas.move import Move
from gaphas.types import Pos

from gaphor.diagram.connectors import Connector
from gaphor.diagram.presentation import connect
from gaphor.diagram.tools.grayout import GrayOutLineHandleMoveMixin
from gaphor.UML.actions.activity import ActivityItem, ActivityParameterNodeItem


@Connector.register(ActivityItem, ActivityParameterNodeItem)
class ActivityParameterNodeConnector:
    def __init__(
        self,
        activity: ActivityItem,
        parameter_node: ActivityParameterNodeItem,
    ) -> None:
        assert activity.diagram is parameter_node.diagram
        self.activity = activity
        self.parameter_node = parameter_node

    def allow(self, handle: Handle, port: Port) -> bool:
        return (
            bool(self.activity.diagram)
            and self.activity.diagram is self.parameter_node.diagram
            and self.parameter_node in self.activity.children
        )

    def connect(self, handle: Handle, port: Port) -> bool:
        return True

    def disconnect(self, handle: Handle) -> None:
        pass


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
