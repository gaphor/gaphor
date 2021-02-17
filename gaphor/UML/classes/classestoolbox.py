"""The definition for the classes section of the toolbox."""

from enum import Enum

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection, namespace_config
from gaphor.diagram.diagramtools import new_item_factory
from gaphor.UML import diagramitems


class AssociationType(Enum):
    COMPOSITE = "composite"
    SHARED = "shared"


def create_association(
    assoc_item: diagramitems.AssociationItem, association_type: AssociationType
) -> None:
    assoc = assoc_item.subject
    assoc.memberEnd.append(assoc_item.model.create(UML.Property))
    assoc.memberEnd.append(assoc_item.model.create(UML.Property))

    assoc_item.head_subject = assoc.memberEnd[0]
    assoc_item.tail_subject = assoc.memberEnd[1]

    UML.model.set_navigability(assoc, assoc_item.head_subject, True)
    assoc_item.head_subject.aggregation = association_type.value


def composite_association_config(assoc_item: diagramitems.AssociationItem) -> None:
    create_association(assoc_item, AssociationType.COMPOSITE)


def shared_association_config(assoc_item: diagramitems.AssociationItem) -> None:
    create_association(assoc_item, AssociationType.SHARED)


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
            "toolbox-composite-association",
            gettext("Composite Association"),
            "gaphor-composite-association-symbolic",
            "<Shift>Z",
            new_item_factory(
                diagramitems.AssociationItem,
                UML.Association,
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
                UML.Association,
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
            "toolbox-dependency",
            gettext("Dependency"),
            "gaphor-dependency-symbolic",
            "<Shift>D",
            new_item_factory(diagramitems.DependencyItem),
        ),
        ToolDef(
            "toolbox-generalization",
            gettext("Generalization"),
            "gaphor-generalization-symbolic",
            "<Shift>G",
            new_item_factory(diagramitems.GeneralizationItem),
        ),
        ToolDef(
            "toolbox-interface-realization",
            gettext("Interface Realization"),
            "gaphor-interface-realization-symbolic",
            "<Shift>I",
            new_item_factory(diagramitems.InterfaceRealizationItem),
        ),
    ),
)
