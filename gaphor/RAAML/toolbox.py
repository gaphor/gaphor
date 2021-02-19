"""The action definition for the RAAML toolbox."""

from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import (
    ToolboxDefinition,
    ToolDef,
    ToolSection,
    general_tools,
    namespace_config,
)
from gaphor.diagram.diagramtools import new_item_factory
from gaphor.SysML import diagramitems as sysml_items
from gaphor.SysML import sysml
from gaphor.UML import diagramitems as uml_items

FTA = ToolSection(
    gettext("Fault Tree Analysis"),
    (
        ToolDef(
            "and",
            gettext("AND"),
            "gaphor-and-symbolic",
            "a",
            new_item_factory(
                sysml_items.BlockItem, sysml.Block, config_func=namespace_config
            ),
        ),
        ToolDef(
            "or",
            gettext("OR"),
            "gaphor-or-symbolic",
            "o",
            new_item_factory(
                sysml_items.BlockItem, sysml.Block, config_func=namespace_config
            ),
        ),
        ToolDef(
            "not",
            gettext("NOT"),
            "gaphor-not-symbolic",
            "n",
            new_item_factory(
                sysml_items.BlockItem, sysml.Block, config_func=namespace_config
            ),
        ),
        ToolDef(
            "seq",
            gettext("SEQ"),
            "gaphor-seq-symbolic",
            "n",
            new_item_factory(
                sysml_items.BlockItem, sysml.Block, config_func=namespace_config
            ),
        ),
        ToolDef(
            "xor",
            gettext("XOR"),
            "gaphor-xor-symbolic",
            "x",
            new_item_factory(
                sysml_items.BlockItem, sysml.Block, config_func=namespace_config
            ),
        ),
        ToolDef(
            "majority-vote",
            gettext("Majority Vote"),
            "gaphor-majority-vote-symbolic",
            "m",
            new_item_factory(
                sysml_items.BlockItem, sysml.Block, config_func=namespace_config
            ),
        ),
        ToolDef(
            "transfer-in",
            gettext("Transfer In"),
            "gaphor-transfer-in-symbolic",
            "t",
            new_item_factory(
                sysml_items.BlockItem, sysml.Block, config_func=namespace_config
            ),
        ),
        ToolDef(
            "inhibit",
            gettext("Inhibit"),
            "gaphor-inhibit-symbolic",
            "i",
            new_item_factory(
                sysml_items.BlockItem, sysml.Block, config_func=namespace_config
            ),
        ),
        ToolDef(
            "basic-event",
            gettext("Basic Event"),
            "gaphor-basic-event-symbolic",
            "b",
            new_item_factory(
                sysml_items.BlockItem, sysml.Block, config_func=namespace_config
            ),
        ),
        ToolDef(
            "conditional-event",
            gettext("Conditional Event"),
            "gaphor-conditional-event-symbolic",
            "b",
            new_item_factory(
                sysml_items.BlockItem, sysml.Block, config_func=namespace_config
            ),
        ),
        ToolDef(
            "dormant-event",
            gettext("Dormant Event"),
            "gaphor-dormant-event-symbolic",
            "b",
            new_item_factory(
                sysml_items.BlockItem, sysml.Block, config_func=namespace_config
            ),
        ),
        ToolDef(
            "house-event",
            gettext("House Event"),
            "gaphor-house-event-symbolic",
            "h",
            new_item_factory(
                sysml_items.BlockItem, sysml.Block, config_func=namespace_config
            ),
        ),
        ToolDef(
            "zero-event",
            gettext("Zero Event"),
            "gaphor-zero-event-symbolic",
            "z",
            new_item_factory(
                sysml_items.BlockItem, sysml.Block, config_func=namespace_config
            ),
        ),
        ToolDef(
            "dependency",
            gettext("Dependency"),
            "gaphor-dependency-symbolic",
            "<Shift>D",
            new_item_factory(uml_items.DependencyItem),
        ),
    ),
)

raaml_toolbox_actions: ToolboxDefinition = (
    general_tools,
    FTA,
)
