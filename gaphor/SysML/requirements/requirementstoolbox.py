"""The definition for the requirements section of the toolbox."""

from gaphas.item import SE

from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import (
    ToolDef,
    ToolSection,
    namespace_config,
    new_item_factory,
)
from gaphor.SysML import diagramitems as sysml_items
from gaphor.SysML import sysml
from gaphor.UML.classes import ContainmentItem

requirements = ToolSection(
    gettext("Requirements"),
    (
        ToolDef(
            "toolbox-requirement",
            gettext("Requirement"),
            "gaphor-requirement-symbolic",
            "r",
            new_item_factory(
                sysml_items.RequirementItem,
                sysml.Requirement,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-satisfy-dependency",
            gettext("Satisfy"),
            "gaphor-satisfy-symbolic",
            "<Shift>I",
            new_item_factory(sysml_items.SatisfyItem),
        ),
        ToolDef(
            "toolbox-derive-reqt-dependency",
            gettext("Derive Requirement"),
            "gaphor-derive-symbolic",
            "<Shift>D",
            new_item_factory(sysml_items.DeriveReqtItem),
        ),
        ToolDef(
            "toolbox-trace-dependency",
            gettext("Trace"),
            "gaphor-trace-symbolic",
            "y",
            new_item_factory(sysml_items.TraceItem),
        ),
        ToolDef(
            "toolbox-refine-dependency",
            gettext("Refine"),
            "gaphor-refine-symbolic",
            None,
            new_item_factory(sysml_items.RefineItem),
        ),
        ToolDef(
            "toolbox-verify-dependency",
            gettext("Verify"),
            "gaphor-verify-symbolic",
            "<Shift>V",
            new_item_factory(sysml_items.VerifyItem),
        ),
        ToolDef(
            "toolbox-containment",
            gettext("Containment"),
            "gaphor-containment-symbolic",
            "<Shift>M",
            new_item_factory(ContainmentItem),
        ),
    ),
)
