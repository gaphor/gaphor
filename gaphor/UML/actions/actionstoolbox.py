"""The definition for the actions section of the toolbox."""

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection
from gaphor.diagram.diagramtools import new_item_factory
from gaphor.UML import diagramitems


def activity_config(new_item):
    subject = new_item.subject
    subject.name = f"New{type(subject).__name__}"
    if subject.activity:
        return

    diagram = new_item.diagram
    package = diagram.namespace

    activities = (
        [i for i in package.ownedType if isinstance(i, UML.Activity)]
        if package
        else diagram.model.lselect(
            lambda e: isinstance(e, UML.Activity) and e.package is None
        )
    )
    if activities:
        subject.activity = activities[0]
    else:
        activity = subject.model.create(UML.Activity)
        activity.name = "Activity"
        activity.package = package
        subject.activity = activity


def partition_config(new_item):
    activity_config(new_item)
    subject = new_item.subject
    new_item.partition = subject

    partition = subject.model.create(UML.ActivityPartition)
    partition.name = "NewActivityPartition"
    partition.activity = subject.activity
    new_item.partition = partition


actions = ToolSection(
    gettext("Actions"),
    (
        ToolDef(
            "toolbox-action",
            gettext("Action"),
            "gaphor-action-symbolic",
            "a",
            new_item_factory(
                diagramitems.ActionItem,
                UML.Action,
                config_func=activity_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-initial-node",
            gettext("Initial node"),
            "gaphor-initial-node-symbolic",
            "j",
            new_item_factory(
                diagramitems.InitialNodeItem,
                UML.InitialNode,
                config_func=activity_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-activity-final-node",
            gettext("Activity final node"),
            "gaphor-activity-final-node-symbolic",
            "f",
            new_item_factory(
                diagramitems.ActivityFinalNodeItem,
                UML.ActivityFinalNode,
                config_func=activity_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-flow-final-node",
            gettext("Flow final node"),
            "gaphor-flow-final-node-symbolic",
            "w",
            new_item_factory(
                diagramitems.FlowFinalNodeItem,
                UML.FlowFinalNode,
                config_func=activity_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-decision-node",
            gettext("Decision/merge node"),
            "gaphor-decision-node-symbolic",
            "g",
            new_item_factory(
                diagramitems.DecisionNodeItem,
                UML.DecisionNode,
                config_func=activity_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-fork-node",
            gettext("Fork/join node"),
            "gaphor-fork-node-symbolic",
            "<Shift>R",
            new_item_factory(
                diagramitems.ForkNodeItem,
                UML.JoinNode,
                config_func=activity_config,
            ),
            handle_index=1,
        ),
        ToolDef(
            "toolbox-object-node",
            gettext("Object node"),
            "gaphor-object-node-symbolic",
            "<Shift>O",
            new_item_factory(
                diagramitems.ObjectNodeItem,
                UML.ObjectNode,
                config_func=activity_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-partition",
            gettext("Partition"),
            "gaphor-partition-symbolic",
            "<Shift>P",
            new_item_factory(
                diagramitems.PartitionItem,
                UML.ActivityPartition,
                config_func=partition_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-flow",
            gettext("Control/object flow"),
            "gaphor-control-flow-symbolic",
            "<Shift>F",
            new_item_factory(diagramitems.FlowItem),
        ),
        ToolDef(
            "toolbox-send-signal-action",
            gettext("Send signal action"),
            "gaphor-send-signal-action-symbolic",
            None,
            new_item_factory(
                diagramitems.SendSignalActionItem,
                UML.SendSignalAction,
                config_func=activity_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-accept-event-action",
            gettext("Accept event action"),
            "gaphor-accept-event-action-symbolic",
            None,
            new_item_factory(
                diagramitems.AcceptEventActionItem,
                UML.AcceptEventAction,
                config_func=activity_config,
            ),
            handle_index=SE,
        ),
    ),
)
