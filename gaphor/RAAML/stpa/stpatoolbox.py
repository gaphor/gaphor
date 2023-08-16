"""The definition for the STPA section of the RAAML toolbox."""

from gaphor.diagram.diagramtoolbox import (
    ToolDef,
    ToolSection,
    new_element_item_factory,
    new_deferred_element_item_factory,
)
from gaphor.i18n import gettext
from gaphor.RAAML import raaml
from gaphor.UML import uml
from gaphor.UML.toolboxconfig import (
    default_namespace,
    named_element_config,
    namespace_config,
)


def loss_config(new_item):
    default_namespace(new_item)
    new_item.subject.name = new_item.diagram.gettext("Loss")


def hazard_config(new_item):
    default_namespace(new_item)
    new_item.subject.name = new_item.diagram.gettext("Hazard")


def abstract_operational_situation_config(new_item):
    default_namespace(new_item)
    new_item.subject.name = new_item.diagram.gettext("Abstract Operational Situation")


stpa = ToolSection(
    "STPA",
    (
        ToolDef(
            "toolbox-generalization",
            gettext("Generalization"),
            "gaphor-generalization-symbolic",
            "<Shift>G",
            new_deferred_element_item_factory(uml.Generalization),
            handle_index=0,
        ),
        ToolDef(
            "loss",
            gettext("Loss"),
            "gaphor-loss-symbolic",
            "<Shift>L",
            new_element_item_factory(raaml.Loss, config_func=loss_config),
        ),
        ToolDef(
            "hazard",
            gettext("Hazard"),
            "gaphor-hazard-symbolic",
            "<Shift>H",
            new_element_item_factory(raaml.Hazard, config_func=hazard_config),
        ),
        ToolDef(
            "situation",
            gettext("Situation"),
            "gaphor-situation-symbolic",
            "s",
            new_element_item_factory(
                raaml.Situation,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "control-structure",
            gettext("Control Structure"),
            "gaphor-control-structure-symbolic",
            "f",
            new_element_item_factory(
                raaml.ControlStructure,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "controller",
            gettext("Controller"),
            "gaphor-controller-symbolic",
            "w",
            new_element_item_factory(
                raaml.Controller,
                config_func=named_element_config,
            ),
        ),
        ToolDef(
            "actuator",
            gettext("Actuator"),
            "gaphor-actuator-symbolic",
            "q",
            new_element_item_factory(
                raaml.Actuator,
                config_func=named_element_config,
            ),
        ),
        ToolDef(
            "controlled-process",
            gettext("Controlled Process"),
            "gaphor-controlled-process-symbolic",
            "<Shift>P",
            new_element_item_factory(
                raaml.ControlledProcess,
                config_func=named_element_config,
            ),
        ),
        ToolDef(
            "abstract-operational-situation",
            gettext("Abstract Operational Situation"),
            "gaphor-abstract-operational-situation-symbolic",
            "<Shift>J",
            new_element_item_factory(
                raaml.AbstractOperationalSituation,
                config_func=abstract_operational_situation_config,
            ),
        ),
        ToolDef(
            "operational-situation",
            gettext("Operational Situation"),
            "gaphor-operational-situation-symbolic",
            "<Shift>O",
            new_element_item_factory(
                raaml.OperationalSituation,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "unsafe-control-action",
            gettext("Unsafe Control Action"),
            "gaphor-unsafe-control-action-symbolic",
            "u",
            new_element_item_factory(
                raaml.UnsafeControlAction,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "relevant-to",
            gettext("Relevant To"),
            "gaphor-relevant-to-symbolic",
            "r",
            new_deferred_element_item_factory(
                raaml.RelevantTo,
            ),
        ),
        ToolDef(
            "control-action",
            gettext("Control Action"),
            "gaphor-control-action-symbolic",
            "<Shift>M",
            new_element_item_factory(
                raaml.ControlAction,
                config_func=namespace_config,
            ),
        ),
    ),
)
