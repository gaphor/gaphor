"""The definition for the STPA section of the RAAML toolbox."""

from gaphor.diagram.diagramtoolbox import (
    ToolDef,
    ToolSection,
    default_namespace,
    namespace_config,
)
from gaphor.diagram.diagramtools import new_item_factory
from gaphor.i18n import gettext
from gaphor.RAAML import diagramitems, raaml
from gaphor.UML import diagramitems as uml_items


def loss_config(new_item):
    default_namespace(new_item)
    new_item.subject.name = "Loss"


def hazard_config(new_item):
    default_namespace(new_item)
    new_item.subject.name = "Hazard"


def abstract_operational_situation_config(new_item):
    default_namespace(new_item)
    new_item.subject.name = "AbstractOperationalSituation"


stpa = ToolSection(
    "STPA",
    (
        ToolDef(
            "toolbox-generalization",
            gettext("Generalization"),
            "gaphor-generalization-symbolic",
            "<Shift>G",
            new_item_factory(uml_items.GeneralizationItem),
        ),
        ToolDef(
            "loss",
            gettext("Loss"),
            "gaphor-loss-symbolic",
            "",
            new_item_factory(
                diagramitems.SituationItem, raaml.Loss, config_func=loss_config
            ),
        ),
        ToolDef(
            "hazard",
            gettext("Hazard"),
            "gaphor-hazard-symbolic",
            "",
            new_item_factory(
                diagramitems.SituationItem, raaml.Hazard, config_func=hazard_config
            ),
        ),
        ToolDef(
            "situation",
            gettext("Situation"),
            "gaphor-situation-symbolic",
            "",
            new_item_factory(
                diagramitems.SituationItem,
                raaml.Situation,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "controller",
            gettext("Controller"),
            "gaphor-controller-symbolic",
            "",
            new_item_factory(uml_items.ClassItem),
        ),
        ToolDef(
            "actuator",
            gettext("Actuator"),
            "gaphor-actuator-symbolic",
            "",
            new_item_factory(uml_items.ClassItem),
        ),
        ToolDef(
            "controlled-process",
            gettext("Controlled Process"),
            "gaphor-controlled-process-symbolic",
            "",
            new_item_factory(uml_items.ClassItem),
        ),
        ToolDef(
            "abstraction-operational-situation",
            gettext("Abstract Operational Situation"),
            "gaphor-abstract-operational-situation-symbolic",
            "",
            new_item_factory(
                diagramitems.OperationalSituationItem,
                raaml.AbstractOperationalSituation,
                config_func=abstract_operational_situation_config,
            ),
        ),
        ToolDef(
            "operational-situation",
            gettext("Operational Situation"),
            "gaphor-operational-situation-symbolic",
            "",
            new_item_factory(
                diagramitems.OperationalSituationItem,
                raaml.OperationalSituation,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "unsafe-control-action",
            gettext("Unsafe Control Action"),
            "gaphor-unsafe-control-action-symbolic",
            "",
            new_item_factory(
                diagramitems.UnsafeControlActionItem,
                raaml.UnsafeControlAction,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "relevant-to",
            gettext("Relevant To"),
            "gaphor-relevant-to-symbolic",
            "",
            new_item_factory(
                diagramitems.RelevantToItem,
                raaml.RelevantTo,
            ),
        ),
        ToolDef(
            "control-action",
            gettext("Control Action"),
            "gaphor-control-action-symbolic",
            "",
            new_item_factory(
                diagramitems.ControlActionItem,
                raaml.ControlAction,
                config_func=namespace_config,
            ),
        ),
    ),
)
