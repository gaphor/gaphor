"""The definition for the profiles section of the toolbox."""

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection, namespace_config
from gaphor.diagram.diagramtools import PlacementTool
from gaphor.UML import diagramitems


def metaclass_config(new_item):
    namespace_config(new_item)
    new_item.subject.name = "Class"


profiles: ToolSection = ToolSection(
    gettext("Profiles"),
    (
        ToolDef(
            "toolbox-profile",
            gettext("Profile"),
            "gaphor-profile-symbolic",
            "r",
            item_factory=PlacementTool.new_item_factory(
                diagramitems.PackageItem,
                UML.Profile,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-metaclass",
            gettext("Metaclass"),
            "gaphor-metaclass-symbolic",
            "m",
            item_factory=PlacementTool.new_item_factory(
                diagramitems.ClassItem, UML.Class, config_func=metaclass_config
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-stereotype",
            gettext("Stereotype"),
            "gaphor-stereotype-symbolic",
            "z",
            item_factory=PlacementTool.new_item_factory(
                diagramitems.ClassItem,
                UML.Stereotype,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-extension",
            gettext("Extension"),
            "gaphor-extension-symbolic",
            "<Shift>E",
            item_factory=PlacementTool.new_item_factory(diagramitems.ExtensionItem),
        ),
        ToolDef(
            "toolbox-import",
            gettext("Import"),
            "gaphor-import-symbolic",
            "<Shift>M",
            item_factory=PlacementTool.new_item_factory(diagramitems.PackageImportItem),
        ),
    ),
)
