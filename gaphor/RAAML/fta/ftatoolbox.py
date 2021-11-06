"""The definition for the FTA section of the RAAML toolbox."""

from functools import partial

from gaphor.diagram.diagramtoolbox import (
    ToolDef,
    ToolSection,
    namespace_config,
    new_item_factory,
)
from gaphor.i18n import gettext
from gaphor.RAAML import diagramitems, raaml
from gaphor.UML import diagramitems as uml_items

fta = ToolSection(
    gettext("Fault Tree Analysis"),
    (
        ToolDef(
            "dependency",
            gettext("Dependency"),
            "gaphor-dependency-symbolic",
            "<Shift>D",
            new_item_factory(uml_items.DependencyItem),
            handle_index=0,
        ),
        ToolDef(
            "and",
            gettext("AND Gate"),
            "gaphor-and-symbolic",
            "a",
            new_item_factory(
                diagramitems.ANDItem,
                raaml.AND,
                config_func=partial(namespace_config, name=gettext("AND")),
            ),
        ),
        ToolDef(
            "or",
            gettext("OR Gate"),
            "gaphor-or-symbolic",
            "o",
            new_item_factory(
                diagramitems.ORItem,
                raaml.OR,
                config_func=partial(namespace_config, name=gettext("OR")),
            ),
        ),
        ToolDef(
            "not",
            gettext("NOT Gate"),
            "gaphor-not-symbolic",
            "n",
            new_item_factory(
                diagramitems.NOTItem,
                raaml.NOT,
                config_func=partial(namespace_config, name=gettext("NOT")),
            ),
        ),
        ToolDef(
            "seq",
            gettext("Sequence Enforcing (SEQ) Gate"),
            "gaphor-seq-symbolic",
            "<Shift>S",
            new_item_factory(
                diagramitems.SEQItem,
                raaml.SEQ,
                config_func=partial(namespace_config, name=gettext("SEQ")),
            ),
        ),
        ToolDef(
            "xor",
            gettext("Exclusive OR Gate"),
            "gaphor-xor-symbolic",
            "x",
            new_item_factory(
                diagramitems.XORItem,
                raaml.XOR,
                config_func=partial(namespace_config, name=gettext("XOR")),
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
                config_func=partial(
                    namespace_config, name=gettext("Majority Vote Gate")
                ),
            ),
        ),
        ToolDef(
            "inhibit",
            gettext("Inhibit Gate"),
            "gaphor-inhibit-symbolic",
            "i",
            new_item_factory(
                diagramitems.InhibitItem,
                raaml.INHIBIT,
                config_func=partial(namespace_config, name=gettext("Inhibit Gate")),
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
                config_func=partial(namespace_config, name=gettext("Transfer In")),
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
                config_func=partial(namespace_config, name=gettext("Transfer Out")),
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
                config_func=partial(namespace_config, name=gettext("Basic Event")),
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
                config_func=partial(
                    namespace_config, name=gettext("Conditional Event")
                ),
            ),
        ),
        ToolDef(
            "undeveloped-event",
            gettext("Undeveloped Event"),
            "gaphor-undeveloped-event-symbolic",
            "<Shift>U",
            new_item_factory(
                diagramitems.UndevelopedEventItem,
                raaml.Undeveloped,
                config_func=partial(
                    namespace_config, name=gettext("Undeveloped Event")
                ),
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
                config_func=partial(namespace_config, name=gettext("Dormant Event")),
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
                config_func=partial(namespace_config, name=gettext("House Event")),
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
                config_func=partial(namespace_config, name=gettext("Zero Event")),
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
                config_func=partial(namespace_config, name=gettext("Top Event")),
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
                config_func=partial(
                    namespace_config, name=gettext("Intermediate Event")
                ),
            ),
        ),
    ),
)
