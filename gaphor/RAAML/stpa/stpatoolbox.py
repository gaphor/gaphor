"""The definition for the STPA section of the RAAML toolbox."""

from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection
from gaphor.diagram.diagramtools import new_item_factory
from gaphor.i18n import gettext
from gaphor.UML import diagramitems as uml_items

stpa = ToolSection(
    "STPA",
    (
        ToolDef(
            "loss",
            gettext("Loss"),
            "gaphor-loss-symbolic",
            "",
            new_item_factory(uml_items.ClassItem),
        ),
        ToolDef(
            "hazard",
            gettext("Hazard"),
            "gaphor-hazard-symbolic",
            "",
            new_item_factory(uml_items.ClassItem),
        ),
        ToolDef(
            "situation",
            gettext("Situation"),
            "gaphor-situation-symbolic",
            "",
            new_item_factory(uml_items.ClassItem),
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
            new_item_factory(uml_items.ClassItem),
        ),
        ToolDef(
            "operational-situation",
            gettext("Operational Situation"),
            "gaphor-operational-situation-symbolic",
            "",
            new_item_factory(uml_items.ClassItem),
        ),
        ToolDef(
            "unsafe-control-action",
            gettext("Unsafe Control Action"),
            "gaphor-unsafe-control-action-symbolic",
            "",
            new_item_factory(uml_items.ClassItem),
        ),
    ),
)
