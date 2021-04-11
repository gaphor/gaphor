"""The action definition for the C4 model toolbox."""

from gaphor.C4Model import c4model, diagramitems
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import (
    ToolboxDefinition,
    ToolDef,
    ToolSection,
    default_namespace,
    general_tools,
    namespace_config,
)
from gaphor.diagram.diagramtools import new_item_factory
from gaphor.UML import diagramitems as uml_items
from gaphor.UML.actions.actionstoolbox import actions
from gaphor.UML.classes.classestoolbox import classes
from gaphor.UML.interactions.interactionstoolbox import interactions
from gaphor.UML.states.statestoolbox import states


def software_system_config(new_item):
    default_namespace(new_item)
    subject = new_item.subject
    subject.type = "Software System"
    subject.name = "NewSoftwareSystem"


def container_config(new_item):
    default_namespace(new_item)
    subject = new_item.subject
    subject.type = "Container"
    subject.name = "NewContainer"


def container_database_config(new_item):
    default_namespace(new_item)
    subject = new_item.subject
    subject.type = "Container"
    subject.technology = "Database"
    subject.name = "NewDatabase"


def component_config(new_item):
    default_namespace(new_item)
    subject = new_item.subject
    subject.type = "Component"
    subject.name = "NewComponent"


c4 = ToolSection(
    gettext("C4 Model"),
    (
        ToolDef(
            "c4-person",
            gettext("Person"),
            "gaphor-c4-person-symbolic",
            "P",
            new_item_factory(
                diagramitems.C4PersonItem,
                c4model.C4Person,
                config_func=namespace_config,
            ),
        ),
        ToolDef(
            "c4-software-system",
            gettext("Software System"),
            "gaphor-c4-software-system-symbolic",
            "<Shift>S",
            new_item_factory(
                diagramitems.C4ContainerItem,
                c4model.C4Container,
                config_func=software_system_config,
            ),
        ),
        ToolDef(
            "c4-container",
            gettext("Container"),
            "gaphor-c4-container-symbolic",
            "o",
            new_item_factory(
                diagramitems.C4ContainerItem,
                c4model.C4Container,
                config_func=container_config,
            ),
        ),
        ToolDef(
            "c4-container-database",
            gettext("Container: Database"),
            "gaphor-c4-database-symbolic",
            "<Shift>B",
            new_item_factory(
                diagramitems.C4ContainerDatabaseItem,
                c4model.C4Database,
                config_func=container_database_config,
            ),
        ),
        ToolDef(
            "c4-component",
            gettext("Component"),
            "gaphor-c4-component-symbolic",
            "<Shift>X",
            new_item_factory(
                diagramitems.C4ContainerItem,
                c4model.C4Container,
                config_func=component_config,
            ),
        ),
        ToolDef(
            "c4-dependency",
            gettext("Dependency"),
            "gaphor-dependency-symbolic",
            "d",
            new_item_factory(uml_items.DependencyItem),
        ),
    ),
)


c4model_toolbox_actions: ToolboxDefinition = (
    general_tools,
    c4,
    classes,
    actions,
    interactions,
    states,
)
