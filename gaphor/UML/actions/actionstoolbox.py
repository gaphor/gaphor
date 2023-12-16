"""The definition for the actions section of the toolbox."""
from functools import partial

from gaphas.item import SE

from gaphor import UML
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection, new_item_factory
from gaphor.i18n import gettext, i18nize
from gaphor.UML import diagramitems
from gaphor.UML.recipes import owner_package
from gaphor.UML.toolboxconfig import namespace_config


def activity_config(new_item, name=None):
    subject = new_item.subject
    if name:
        subject.name = new_item.diagram.gettext("New {name}").format(name=name)
    if subject.activity:
        return

    diagram = new_item.diagram

    if owner_activity := UML.recipes.owner_of_type(diagram, UML.Activity):
        subject.activity = owner_activity
        return

    package = owner_package(diagram.owner)

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
        activity.name = new_item.diagram.gettext("Activity")
        activity.package = package
        subject.activity = activity


def partition_config(new_item):
    activity_config(new_item)
    subject = new_item.subject
    subject.name = new_item.diagram.gettext("Swimlane One")
    new_item.partition = subject

    partition = subject.model.create(UML.ActivityPartition)
    partition.name = new_item.diagram.gettext("Swimlane Two")
    partition.activity = subject.activity
    new_item.partition = partition


def value_specification_action_config(new_item):
    activity_config(new_item, i18nize("ValueSpecificationAction"))
    new_item.subject.value = "1"


actions = ToolSection(
    gettext("Actions"),
    (
        ToolDef(
            "toolbox-activity",
            gettext("Activity"),
            "gaphor-activity-symbolic",
            None,
            new_item_factory(
                diagramitems.ActivityItem,
                UML.Activity,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-action",
            gettext("Action"),
            "gaphor-action-symbolic",
            "a",
            new_item_factory(
                diagramitems.ActionItem,
                UML.Action,
                config_func=partial(activity_config, name=i18nize("Action")),
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-call-behavior-action",
            gettext("Call behavior action"),
            "gaphor-call-behavior-action-symbolic",
            "<Alt>a",
            new_item_factory(
                diagramitems.CallBehaviorActionItem,
                UML.CallBehaviorAction,
                config_func=partial(
                    activity_config, name=i18nize("CallBehaviorAction")
                ),
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-value-specification-action",
            gettext("Value specification action"),
            "gaphor-value-specification-action-symbolic",
            "<Alt>v",
            new_item_factory(
                diagramitems.ValueSpecificationActionItem,
                UML.ValueSpecificationAction,
                config_func=value_specification_action_config,
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
                config_func=partial(activity_config, name=i18nize("Object node")),
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-partition",
            gettext("Swimlane"),
            "gaphor-activity-partition-symbolic",
            "<Shift>P",
            new_item_factory(
                diagramitems.PartitionItem,
                UML.ActivityPartition,
                config_func=partition_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-control-flow",
            gettext("Control flow"),
            "gaphor-control-flow-symbolic",
            "<Shift>F",
            new_item_factory(diagramitems.ControlFlowItem),
        ),
        ToolDef(
            "toolbox-object-flow",
            gettext("Object flow"),
            "gaphor-object-flow-symbolic",
            "<Shift>Y",
            new_item_factory(diagramitems.ObjectFlowItem),
        ),
        ToolDef(
            "toolbox-send-signal-action",
            gettext("Send signal action"),
            "gaphor-send-signal-action-symbolic",
            None,
            new_item_factory(
                diagramitems.SendSignalActionItem,
                UML.SendSignalAction,
                config_func=partial(activity_config, name=i18nize("Send signal")),
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
                config_func=partial(activity_config, name=i18nize("Accept event")),
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-input-pin",
            gettext("Input pin"),
            "gaphor-input-pin-symbolic",
            None,
            new_item_factory(diagramitems.InputPinItem),
        ),
        ToolDef(
            "toolbox-output-pin",
            gettext("Output pin"),
            "gaphor-output-pin-symbolic",
            None,
            new_item_factory(diagramitems.OutputPinItem),
        ),
    ),
)
