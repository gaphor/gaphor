"""The action definition for the SysML toolbox."""

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolboxDefinition, ToolDef, ToolSection
from gaphor.diagram.diagramtools import PlacementTool
from gaphor.SysML import diagramitems as sysml_items
from gaphor.SysML import sysml
from gaphor.UML import diagramitems as uml_items
from gaphor.UML.toolbox import (
    actions,
    composite_association_config,
    general,
    interactions,
    namespace_config,
    shared_association_config,
    states,
    use_cases,
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

internal_blocks = ToolSection(
    gettext("Internal Blocks"),
    (
        ToolDef(
            "toolbox-connector",
            gettext("Connector"),
            "gaphor-connector-symbolic",
            "<Shift>C",
            PlacementTool.new_item_factory(uml_items.ConnectorItem),
        ),
        ToolDef(
            "toolbox-property",
            gettext("Property"),
            "gaphor-property-symbolic",
            "o",
            PlacementTool.new_item_factory(
                sysml_items.PropertyItem, UML.Property, config_func=namespace_config
            ),
        ),
        ToolDef(
            "toolbox-proxy-port",
            gettext("Proxy Port"),
            "gaphor-proxyport-symbolic",
            "x",
            PlacementTool.new_item_factory(sysml_items.ProxyPortItem),
        ),
    ),
)

requirements = ToolSection(
    gettext("Requirements"),
    (
        ToolDef(
            "toolbox-requirement",
            gettext("Requirement"),
            "gaphor-requirement-symbolic",
            "r",
            item_factory=PlacementTool.new_item_factory(
                sysml_items.RequirementItem,
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
            PlacementTool.new_item_factory(sysml_items.SatisfyItem),
        ),
        ToolDef(
            "toolbox-derive-reqt-dependency",
            gettext("Derive Reqt"),
            "gaphor-derive-symbolic",
            "<Shift>D",
            PlacementTool.new_item_factory(sysml_items.DeriveReqtItem),
        ),
        ToolDef(
            "toolbox-trace-dependency",
            gettext("Trace"),
            "gaphor-trace-symbolic",
            "<Shift>E",
            PlacementTool.new_item_factory(sysml_items.TraceItem),
        ),
        ToolDef(
            "toolbox-refine-dependency",
            gettext("Refine"),
            "gaphor-refine-symbolic",
            "<Shift>N",
            PlacementTool.new_item_factory(sysml_items.RefineItem),
        ),
        ToolDef(
            "toolbox-verify-dependency",
            gettext("Verify"),
            "gaphor-verify-symbolic",
            "<Shift>V",
            PlacementTool.new_item_factory(sysml_items.VerifyItem),
        ),
    ),
)

sysml_toolbox_actions: ToolboxDefinition = (
    general,
    blocks,
    internal_blocks,
    requirements,
    actions,
    interactions,
    states,
    use_cases,
)
