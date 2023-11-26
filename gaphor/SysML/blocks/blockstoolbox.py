"""The definition for the blocks section of the toolbox."""

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection, new_item_factory
from gaphor.SysML import diagramitems as sysml_items
from gaphor.SysML import sysml
from gaphor.UML import diagramitems as uml_items
from gaphor.UML.classes.classestoolbox import (
    composite_association_config,
    direct_association_config,
    shared_association_config,
)
from gaphor.UML.toolboxconfig import namespace_config


def sysml_enumeration_config(new_item: uml_items.EnumerationItem, name=None):
    namespace_config(new_item, name)
    new_item.as_sysml_value_type = True


blocks = ToolSection(
    gettext("Blocks"),
    (
        ToolDef(
            "toolbox-block",
            gettext("Block"),
            "gaphor-block-symbolic",
            "<Shift>B",
            new_item_factory(
                sysml_items.BlockItem, sysml.Block, config_func=namespace_config
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-interfaceblock",
            gettext("InterfaceBlock"),
            "gaphor-interface-block-symbolic",
            None,
            new_item_factory(
                sysml_items.InterfaceBlockItem,
                sysml.InterfaceBlock,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-package",
            gettext("Package"),
            "gaphor-package-symbolic",
            "p",
            new_item_factory(
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
            new_item_factory(
                uml_items.AssociationItem,
                config_func=composite_association_config,
            ),
        ),
        ToolDef(
            "toolbox-shared-association",
            gettext("Shared Association"),
            "gaphor-shared-association-symbolic",
            "<Shift>Q",
            new_item_factory(
                uml_items.AssociationItem,
                config_func=shared_association_config,
            ),
        ),
        ToolDef(
            "toolbox-association",
            gettext("Association"),
            "gaphor-association-symbolic",
            "<Shift>A",
            new_item_factory(uml_items.AssociationItem),
        ),
        ToolDef(
            "toolbox-direct-association",
            gettext("Direct Association"),
            "gaphor-direct-association-symbolic",
            None,
            new_item_factory(
                uml_items.AssociationItem,
                config_func=direct_association_config,
            ),
        ),
        ToolDef(
            "toolbox-generalization",
            gettext("Generalization"),
            "gaphor-generalization-symbolic",
            "<Shift>G",
            new_item_factory(uml_items.GeneralizationItem),
        ),
        ToolDef(
            "toolbox-value-type",
            gettext("ValueType"),
            "gaphor-value-type-symbolic",
            "<Shift>L",
            new_item_factory(
                uml_items.DataTypeItem,
                sysml.ValueType,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "toolbox-enumeration",
            gettext("Enumeration"),
            "gaphor-enumeration-symbolic",
            "<Shift>W",
            new_item_factory(
                uml_items.EnumerationItem,
                UML.Enumeration,
                config_func=sysml_enumeration_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-primitive",
            gettext("Primitive"),
            "gaphor-primitive-type-symbolic",
            "<Shift>H",
            new_item_factory(
                uml_items.DataTypeItem,
                UML.PrimitiveType,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
    ),
)
