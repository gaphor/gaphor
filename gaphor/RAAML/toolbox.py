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
from gaphor.RAAML import diagramitems, raaml
from gaphor.UML import diagramitems as uml_items

FTA = ToolSection(
    gettext("Fault Tree Analysis"),
    (
        ToolDef(
            "dependency",
            gettext("Dependency"),
            "gaphor-dependency-symbolic",
            "<Shift>D",
            new_item_factory(uml_items.DependencyItem),
        ),
        ToolDef(
            "and",
            gettext("AND Gate"),
            "gaphor-and-symbolic",
            "a",
            new_item_factory(
                diagramitems.ANDItem, raaml.AND, config_func=namespace_config
            ),
        ),
        ToolDef(
            "or",
            gettext("OR Gate"),
            "gaphor-or-symbolic",
            "o",
            new_item_factory(
                diagramitems.ORItem, raaml.OR, config_func=namespace_config
            ),
        ),
        ToolDef(
            "not",
            gettext("NOT Gate"),
            "gaphor-not-symbolic",
            "n",
            new_item_factory(
                diagramitems.NOTItem, raaml.NOT, config_func=namespace_config
            ),
        ),
        ToolDef(
            "seq",
            gettext("Sequence Enforcing (SEQ) Gate"),
            "gaphor-seq-symbolic",
            "s",
            new_item_factory(
                diagramitems.SEQItem, raaml.SEQ, config_func=namespace_config
            ),
        ),
        ToolDef(
            "xor",
            gettext("Exclusive OR Gate"),
            "gaphor-xor-symbolic",
            "x",
            new_item_factory(
                diagramitems.XORItem, raaml.XOR, config_func=namespace_config
            ),
        ),
        ToolDef(
            "majority_vote",
            gettext("Majority Vote Gate"),
            "gaphor-majority_vote-symbolic",
            "m",
            new_item_factory(
                diagramitems.MajorityVoteItem,
                raaml.MAJORITY_VOTE,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "inhibit",
            gettext("Inhibit Gate"),
            "gaphor-inhibit-symbolic",
            "i",
            new_item_factory(
                diagramitems.InhibitItem, raaml.INHIBIT, config_func=namespace_config
            ),
        ),
        ToolDef(
            "transfer-in",
            gettext("Transfer In"),
            "gaphor-transfer-in-symbolic",
            "t",
            new_item_factory(
                diagramitems.TransferInItem,
                raaml.TransferIn,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "transfer-out",
            gettext("Transfer Out"),
            "gaphor-transfer-out-symbolic",
            "<Shift>T",
            new_item_factory(
                diagramitems.TransferOutItem,
                raaml.TransferOut,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "basic-event",
            gettext("Basic Event"),
            "gaphor-basic-event-symbolic",
            "<Shift>B",
            new_item_factory(
                diagramitems.BasicEventItem,
                raaml.BasicEvent,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "conditional-event",
            gettext("Conditional Event"),
            "gaphor-conditional-event-symbolic",
            "c",
            new_item_factory(
                diagramitems.ConditionalEventItem,
                raaml.ConditionalEvent,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "undeveloped-event",
            gettext("Undeveloped Event"),
            "gaphor-undeveloped-event-symbolic",
            "u",
            new_item_factory(
                diagramitems.UndevelopedEventItem,
                raaml.Undeveloped,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "dormant-event",
            gettext("Dormant Event"),
            "gaphor-dormant-event-symbolic",
            "d",
            new_item_factory(
                diagramitems.DormantEventItem,
                raaml.DormantEvent,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "house-event",
            gettext("House Event"),
            "gaphor-house-event-symbolic",
            "h",
            new_item_factory(
                diagramitems.HouseEventItem,
                raaml.HouseEvent,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "zero-event",
            gettext("Zero Event"),
            "gaphor-zero-event-symbolic",
            "z",
            new_item_factory(
                diagramitems.ZeroEventItem,
                raaml.ZeroEvent,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "top-event",
            gettext("Top Event"),
            "gaphor-top-event-symbolic",
            "p",
            new_item_factory(
                diagramitems.TopEventItem,
                raaml.TopEvent,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "intermediate-event",
            gettext("Intermediate Event"),
            "gaphor-intermediate-event-symbolic",
            "<Shift>I",
            new_item_factory(
                diagramitems.IntermediateEventItem,
                raaml.IntermediateEvent,
                config_func=namespace_config,
            ),
        ),
    ),
)

raaml_toolbox_actions: ToolboxDefinition = (
    general_tools,
    FTA,
)
