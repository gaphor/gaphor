"""The definition for the classes section of the toolbox."""

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection, new_item_factory
from gaphor.UML import diagramitems
from gaphor.UML.toolboxconfig import namespace_config


def composite_association_config(assoc_item: diagramitems.AssociationItem) -> None:
    assoc_item.preferred_aggregation = "composite"


def shared_association_config(assoc_item: diagramitems.AssociationItem) -> None:
    assoc_item.preferred_aggregation = "shared"


def direct_association_config(assoc_item: diagramitems.AssociationItem) -> None:
    assoc_item.preferred_tail_navigability = "navigable"


classes = ToolSection(
    gettext("Classes"),
    (
        ToolDef(
            "toolbox-class",
            gettext("Class"),
            "gaphor-class-symbolic",
            "c",
            new_item_factory(
                diagramitems.ClassItem, UML.Class, config_func=namespace_config
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-interface",
            gettext("Interface"),
            "gaphor-interface-symbolic",
            "i",
            new_item_factory(
                diagramitems.InterfaceItem,
                UML.Interface,
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
                diagramitems.PackageItem,
                UML.Package,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-component",
            gettext("Component"),
            "gaphor-component-symbolic",
            "o",
            new_item_factory(
                diagramitems.ComponentItem,
                UML.Component,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-containment",
            gettext("Containment"),
            "gaphor-containment-symbolic",
            "<Shift>C",
            new_item_factory(diagramitems.ContainmentItem),
        ),
        ToolDef(
            "toolbox-composite-association",
            gettext("Composite Association"),
            "gaphor-composite-association-symbolic",
            "<Shift>Z",
            new_item_factory(
                diagramitems.AssociationItem,
                config_func=composite_association_config,
            ),
        ),
        ToolDef(
            "toolbox-shared-association",
            gettext("Shared Association"),
            "gaphor-shared-association-symbolic",
            "<Shift>Q",
            new_item_factory(
                diagramitems.AssociationItem,
                config_func=shared_association_config,
            ),
        ),
        ToolDef(
            "toolbox-association",
            gettext("Association"),
            "gaphor-association-symbolic",
            "<Shift>A",
            new_item_factory(diagramitems.AssociationItem),
        ),
        ToolDef(
            "toolbox-direct-association",
            gettext("Direct Association"),
            "gaphor-direct-association-symbolic",
            None,
            new_item_factory(
                diagramitems.AssociationItem,
                config_func=direct_association_config,
            ),
        ),
        ToolDef(
            "toolbox-dependency",
            gettext("Dependency"),
            "gaphor-dependency-symbolic",
            "<Shift>D",
            new_item_factory(diagramitems.DependencyItem),
            handle_index=0,
        ),
        ToolDef(
            "toolbox-generalization",
            gettext("Generalization"),
            "gaphor-generalization-symbolic",
            "<Shift>G",
            new_item_factory(diagramitems.GeneralizationItem),
            handle_index=0,
        ),
        ToolDef(
            "toolbox-interface-realization",
            gettext("Interface Realization"),
            "gaphor-interface-realization-symbolic",
            "<Shift>I",
            new_item_factory(diagramitems.InterfaceRealizationItem),
        ),
        ToolDef(
            "toolbox-data-type",
            gettext("DataType"),
            "gaphor-data-type-symbolic",
            "<Shift>L",
            new_item_factory(
                diagramitems.DataTypeItem,
                UML.DataType,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-enumeration",
            gettext("Enumeration"),
            "gaphor-enumeration-symbolic",
            "<Shift>W",
            new_item_factory(
                diagramitems.EnumerationItem,
                UML.Enumeration,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-primitive",
            gettext("Primitive"),
            "gaphor-primitive-type-symbolic",
            "<Shift>H",
            new_item_factory(
                diagramitems.DataTypeItem,
                UML.PrimitiveType,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
    ),
)
