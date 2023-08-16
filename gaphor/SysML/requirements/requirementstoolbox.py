"""The definition for the requirements section of the toolbox."""

from gaphas.item import SE

from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import (
    ToolDef,
    ToolSection,
    new_item_factory,
    new_element_item_factory,
    new_deferred_element_item_factory,
)
from gaphor.SysML import sysml
from gaphor.UML.classes import ContainmentItem
from gaphor.UML.toolboxconfig import namespace_config

requirements = ToolSection(
    gettext("Requirements"),
    (
        ToolDef(
            "toolbox-requirement",
            gettext("Requirement"),
            "gaphor-requirement-symbolic",
            "r",
            new_element_item_factory(
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
            new_deferred_element_item_factory(sysml.Satisfy),
        ),
        ToolDef(
            "toolbox-derive-reqt-dependency",
            gettext("Derive Requirement"),
            "gaphor-derive-reqt-symbolic",
            "<Shift>D",
            new_deferred_element_item_factory(sysml.DeriveReqt),
        ),
        ToolDef(
            "toolbox-trace-dependency",
            gettext("Trace"),
            "gaphor-trace-symbolic",
            "y",
            new_deferred_element_item_factory(sysml.Trace),
        ),
        ToolDef(
            "toolbox-refine-dependency",
            gettext("Refine"),
            "gaphor-refine-symbolic",
            None,
            new_deferred_element_item_factory(sysml.Refine),
        ),
        ToolDef(
            "toolbox-verify-dependency",
            gettext("Verify"),
            "gaphor-verify-symbolic",
            "<Shift>V",
            new_deferred_element_item_factory(sysml.Verify),
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
