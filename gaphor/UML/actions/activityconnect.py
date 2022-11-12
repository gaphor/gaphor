from gaphas.connector import Handle, Port

from gaphor.diagram.connectors import Connector
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
