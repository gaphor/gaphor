"""The definition for the profiles section of the toolbox."""

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection, new_item_factory
from gaphor.UML import diagramitems
from gaphor.UML.toolboxconfig import namespace_config


def metaclass_config(new_item):
    namespace_config(new_item)
    new_item.subject.name = new_item.diagram.gettext("Class")


profiles: ToolSection = ToolSection(
    gettext("Profiles"),
    (
        ToolDef(
            "toolbox-profile",
            gettext("Profile"),
            "gaphor-profile-symbolic",
            "r",
            new_item_factory(
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
            new_item_factory(
                diagramitems.ClassItem, UML.Class, config_func=metaclass_config
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-stereotype",
            gettext("Stereotype"),
            "gaphor-stereotype-symbolic",
            "z",
            new_item_factory(
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
            new_item_factory(diagramitems.ExtensionItem),
        ),
        ToolDef(
            "toolbox-import",
            gettext("Import"),
            "gaphor-import-symbolic",
            "<Shift>M",
            new_item_factory(diagramitems.PackageImportItem),
            handle_index=0,
        ),
    ),
)
