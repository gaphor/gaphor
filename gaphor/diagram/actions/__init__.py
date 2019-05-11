from .action import ActionItem, SendSignalActionItem, AcceptEventActionItem
from .activitynodes import (
    ActivityNodeItem,
    ActivityFinalNodeItem,
    FlowFinalNodeItem,
    ForkNodeItem,
    DecisionNodeItem,
    InitialNodeItem,
)
from .flow import FlowItem
from .objectnode import ObjectNodeItem
from .partition import PartitionItem


def _load():
    from . import actionsgrouping, flowconnect, partitionpage, actionspropertypages


_load()
