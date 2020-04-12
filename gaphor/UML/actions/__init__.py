from gaphor.UML.actions.action import (
    AcceptEventActionItem,
    ActionItem,
    SendSignalActionItem,
)
from gaphor.UML.actions.activitynodes import (
    ActivityFinalNodeItem,
    ActivityNodeItem,
    DecisionNodeItem,
    FlowFinalNodeItem,
    ForkNodeItem,
    InitialNodeItem,
)
from gaphor.UML.actions.flow import FlowItem
from gaphor.UML.actions.objectnode import ObjectNodeItem
from gaphor.UML.actions.partition import PartitionItem


def _load():
    from gaphor.UML.actions import (
        actionsgrouping,
        flowconnect,
        partitionpage,
        actionseditors,
        actionspropertypages,
    )


_load()
