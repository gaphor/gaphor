"""The definition for the blocks section of the toolbox."""

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection, namespace_config
from gaphor.diagram.diagramtools import PlacementTool
from gaphor.SysML import diagramitems as sysml_items
from gaphor.SysML import sysml
from gaphor.UML import diagramitems as uml_items
from gaphor.UML.classes.classestoolbox import (
    composite_association_config,
    shared_association_config,
)

blocks = ToolSection(
    gettext("Blocks"),
    (
        ToolDef(
            "toolbox-block",
            gettext("Block"),
            "gaphor-block-symbolic",
            "l",
            item_factory=PlacementTool.new_item_factory(
                sysml_items.BlockItem, sysml.Block, config_func=namespace_config
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-package",
            gettext("Package"),
            "gaphor-package-symbolic",
            "p",
            PlacementTool.new_item_factory(
                uml_items.PackageItem,
                UML.Package,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-composite-association",
            gettext("Composite Association"),
            "gaphor-composite-association-symbolic",
            "<Shift>Z",
            PlacementTool.new_item_factory(
                uml_items.AssociationItem,
                UML.Association,
                config_func=composite_association_config,
            ),
        ),
        ToolDef(
            "toolbox-shared-association",
            gettext("Shared Association"),
            "gaphor-shared-association-symbolic",
            "<Shift>Q",
            PlacementTool.new_item_factory(
                uml_items.AssociationItem,
                UML.Association,
                config_func=shared_association_config,
            ),
        ),
        ToolDef(
            "toolbox-association",
            gettext("Association"),
            "gaphor-association-symbolic",
            "<Shift>A",
            PlacementTool.new_item_factory(uml_items.AssociationItem),
        ),
        ToolDef(
            "toolbox-generalization",
            gettext("Generalization"),
            "gaphor-generalization-symbolic",
            "<Shift>G",
            PlacementTool.new_item_factory(uml_items.GeneralizationItem),
        ),
    ),
)
