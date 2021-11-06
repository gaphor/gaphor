"""The definition for the use cases section of the toolbox."""

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import (
    ToolDef,
    ToolSection,
    namespace_config,
    new_item_factory,
)
from gaphor.UML import diagramitems

use_cases = ToolSection(
    gettext("Use Cases"),
    (
        ToolDef(
            "toolbox-use-case",
            gettext("Use case"),
            "gaphor-use-case-symbolic",
            "u",
            new_item_factory(
                diagramitems.UseCaseItem,
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
            new_item_factory(
                diagramitems.ActorItem,
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
            new_item_factory(diagramitems.AssociationItem),
        ),
        ToolDef(
            "toolbox-include",
            gettext("Include"),
            "gaphor-include-symbolic",
            "<Shift>U",
            new_item_factory(diagramitems.IncludeItem),
            handle_index=0,
        ),
        ToolDef(
            "toolbox-extend",
            gettext("Extend"),
            "gaphor-extend-symbolic",
            "<Shift>X",
            new_item_factory(diagramitems.ExtendItem),
            handle_index=0,
        ),
    ),
)
