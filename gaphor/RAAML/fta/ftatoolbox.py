"""The definition for the FTA section of the RAAML toolbox."""

from functools import partial

from gaphor.diagram.diagramtoolbox import (
    ToolDef,
    ToolSection,
    new_element_item_factory,
    new_deferred_element_item_factory,
)
from gaphor.i18n import gettext, i18nize
from gaphor.RAAML import raaml
from gaphor.UML import uml
from gaphor.UML.toolboxconfig import named_element_config, namespace_config

fta = ToolSection(
    gettext("Fault Tree Analysis"),
    (
        ToolDef(
            "dependency",
            gettext("Dependency"),
            "gaphor-dependency-symbolic",
            "<Shift>D",
            new_deferred_element_item_factory(uml.Dependency),
            handle_index=0,
        ),
        ToolDef(
            "and",
            gettext("AND Gate"),
            "gaphor-and-symbolic",
            "a",
            new_element_item_factory(
                raaml.AND,
                config_func=partial(namespace_config, name=i18nize("AND")),
            ),
        ),
        ToolDef(
            "or",
            gettext("OR Gate"),
            "gaphor-or-symbolic",
            "o",
            new_element_item_factory(
                raaml.OR,
                config_func=partial(namespace_config, name=i18nize("OR")),
            ),
        ),
        ToolDef(
            "not",
            gettext("NOT Gate"),
            "gaphor-not-symbolic",
            "n",
            new_element_item_factory(
                raaml.NOT,
                config_func=partial(namespace_config, name=i18nize("NOT")),
            ),
        ),
        ToolDef(
            "seq",
            gettext("Sequence Enforcing (SEQ) Gate"),
            "gaphor-seq-symbolic",
            "<Shift>S",
            new_element_item_factory(
                raaml.SEQ,
                config_func=partial(namespace_config, name=i18nize("SEQ")),
            ),
        ),
        ToolDef(
            "xor",
            gettext("Exclusive OR Gate"),
            "gaphor-xor-symbolic",
            "x",
            new_element_item_factory(
                raaml.XOR,
                config_func=partial(namespace_config, name=i18nize("XOR")),
            ),
        ),
        ToolDef(
            "majority_vote",
            gettext("Majority Vote Gate"),
            "gaphor-majority_vote-symbolic",
            "m",
            new_element_item_factory(
                raaml.MAJORITY_VOTE,
                config_func=partial(
                    namespace_config, name=i18nize("Majority Vote Gate")
                ),
            ),
        ),
        ToolDef(
            "inhibit",
            gettext("Inhibit Gate"),
            "gaphor-inhibit-symbolic",
            "i",
            new_element_item_factory(
                raaml.INHIBIT,
                config_func=partial(namespace_config, name=i18nize("Inhibit Gate")),
            ),
        ),
        ToolDef(
            "transfer-in",
            gettext("Transfer In"),
            "gaphor-transfer-in-symbolic",
            "t",
            new_element_item_factory(
                raaml.TransferIn,
                config_func=partial(named_element_config, name=i18nize("Transfer In")),
            ),
        ),
        ToolDef(
            "transfer-out",
            gettext("Transfer Out"),
            "gaphor-transfer-out-symbolic",
            "<Shift>T",
            new_element_item_factory(
                raaml.TransferOut,
                config_func=partial(namespace_config, name=i18nize("Transfer Out")),
            ),
        ),
        ToolDef(
            "basic-event",
            gettext("Basic Event"),
            "gaphor-basic-event-symbolic",
            "<Shift>B",
            new_element_item_factory(
                raaml.BasicEvent,
                config_func=partial(namespace_config, name=i18nize("Basic Event")),
            ),
        ),
        ToolDef(
            "conditional-event",
            gettext("Conditional Event"),
            "gaphor-conditional-event-symbolic",
            "c",
            new_element_item_factory(
                raaml.ConditionalEvent,
                config_func=partial(
                    namespace_config, name=i18nize("Conditional Event")
                ),
            ),
        ),
        ToolDef(
            "undeveloped-event",
            gettext("Undeveloped Event"),
            "gaphor-undeveloped-event-symbolic",
            "<Shift>U",
            new_element_item_factory(
                raaml.Undeveloped,
                config_func=partial(
                    named_element_config, name=i18nize("Undeveloped Event")
                ),
            ),
        ),
        ToolDef(
            "dormant-event",
            gettext("Dormant Event"),
            "gaphor-dormant-event-symbolic",
            "d",
            new_element_item_factory(
                raaml.DormantEvent,
                config_func=partial(namespace_config, name=i18nize("Dormant Event")),
            ),
        ),
        ToolDef(
            "house-event",
            gettext("House Event"),
            "gaphor-house-event-symbolic",
            "h",
            new_element_item_factory(
                raaml.HouseEvent,
                config_func=partial(namespace_config, name=i18nize("House Event")),
            ),
        ),
        ToolDef(
            "zero-event",
            gettext("Zero Event"),
            "gaphor-zero-event-symbolic",
            "z",
            new_element_item_factory(
                raaml.ZeroEvent,
                config_func=partial(namespace_config, name=i18nize("Zero Event")),
            ),
        ),
        ToolDef(
            "top-event",
            gettext("Top Event"),
            "gaphor-top-event-symbolic",
            "p",
            new_element_item_factory(
                raaml.TopEvent,
                config_func=partial(namespace_config, name=i18nize("Top Event")),
            ),
        ),
        ToolDef(
            "intermediate-event",
            gettext("Intermediate Event"),
            "gaphor-intermediate-event-symbolic",
            "<Shift>I",
            new_element_item_factory(
                raaml.IntermediateEvent,
                config_func=partial(
                    namespace_config, name=i18nize("Intermediate Event")
                ),
            ),
        ),
    ),
)
