"""The definition for the classes section of the toolbox."""

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import (
    ToolDef,
    ToolSection,
    new_item_factory,
    new_element_item_factory,
    new_deferred_element_item_factory,
)
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
            new_element_item_factory(UML.Class, config_func=namespace_config),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-interface",
            gettext("Interface"),
            "gaphor-interface-symbolic",
            "i",
            new_element_item_factory(
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
            new_element_item_factory(
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
            new_element_item_factory(
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
            new_deferred_element_item_factory(
                UML.Association,
                config_func=composite_association_config,
            ),
        ),
        ToolDef(
            "toolbox-shared-association",
            gettext("Shared Association"),
            "gaphor-shared-association-symbolic",
            "<Shift>Q",
            new_deferred_element_item_factory(
                UML.Association,
                config_func=shared_association_config,
            ),
        ),
        ToolDef(
            "toolbox-association",
            gettext("Association"),
            "gaphor-association-symbolic",
            "<Shift>A",
            new_deferred_element_item_factory(UML.Association),
        ),
        ToolDef(
            "toolbox-direct-association",
            gettext("Direct Association"),
            "gaphor-direct-association-symbolic",
            None,
            new_deferred_element_item_factory(
                UML.Association,
                config_func=direct_association_config,
            ),
        ),
        ToolDef(
            "toolbox-dependency",
            gettext("Dependency"),
            "gaphor-dependency-symbolic",
            "<Shift>D",
            new_deferred_element_item_factory(UML.Dependency),
            handle_index=0,
        ),
        ToolDef(
            "toolbox-generalization",
            gettext("Generalization"),
            "gaphor-generalization-symbolic",
            "<Shift>G",
            new_deferred_element_item_factory(UML.Generalization),
            handle_index=0,
        ),
        ToolDef(
            "toolbox-interface-realization",
            gettext("Interface Realization"),
            "gaphor-interface-realization-symbolic",
            "<Shift>I",
            new_deferred_element_item_factory(UML.InterfaceRealization),
        ),
        ToolDef(
            "toolbox-data-type",
            gettext("DataType"),
            "gaphor-data-type-symbolic",
            "<Shift>L",
            new_element_item_factory(
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
            new_element_item_factory(
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
            new_element_item_factory(
                UML.PrimitiveType,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
    ),
)
