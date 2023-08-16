"""The definition for the use cases section of the toolbox."""

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import (
    ToolDef,
    ToolSection,
    new_element_item_factory,
    new_deferred_element_item_factory,
)
from gaphor.UML.toolboxconfig import namespace_config

use_cases = ToolSection(
    gettext("Use Cases"),
    (
        ToolDef(
            "toolbox-use-case",
            gettext("Use case"),
            "gaphor-use-case-symbolic",
            "u",
            new_element_item_factory(
                UML.UseCase,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-actor",
            gettext("Actor"),
            "gaphor-actor-symbolic",
            "t",
            new_element_item_factory(
                UML.Actor,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-use-case-association",
            gettext("Association"),
            "gaphor-association-symbolic",
            "<Shift>J",
            new_deferred_element_item_factory(UML.Association),
        ),
        ToolDef(
            "toolbox-include",
            gettext("Include"),
            "gaphor-include-symbolic",
            "<Shift>U",
            new_deferred_element_item_factory(UML.Include),
            handle_index=0,
        ),
        ToolDef(
            "toolbox-extend",
            gettext("Extend"),
            "gaphor-extend-symbolic",
            "<Shift>X",
            new_deferred_element_item_factory(UML.Extend),
            handle_index=0,
        ),
    ),
)
