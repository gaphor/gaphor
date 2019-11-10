from gaphor.diagram.actions.action import (
    AcceptEventActionItem,
    ActionItem,
    SendSignalActionItem,
)
from gaphor.diagram.actions.activitynodes import (
    ActivityFinalNodeItem,
    ActivityNodeItem,
    DecisionNodeItem,
    FlowFinalNodeItem,
    ForkNodeItem,
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
