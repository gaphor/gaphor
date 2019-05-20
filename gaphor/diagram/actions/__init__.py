from gaphor.diagram.actions.action import (
    ActionItem,
    SendSignalActionItem,
    AcceptEventActionItem,
)
from gaphor.diagram.actions.activitynodes import (
    ActivityNodeItem,
    ActivityFinalNodeItem,
    FlowFinalNodeItem,
    ForkNodeItem,
    DecisionNodeItem,
    InitialNodeItem,
)
from gaphor.diagram.actions.flow import FlowItem
from gaphor.diagram.actions.objectnode import ObjectNodeItem
from gaphor.diagram.actions.partition import PartitionItem


def _load():
    from gaphor.diagram.actions import (
        actionsgrouping,
        flowconnect,
        partitionpage,
        actionseditors,
        actionspropertypages,
    )


_load()
