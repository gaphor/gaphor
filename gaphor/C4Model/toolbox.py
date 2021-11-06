"""The action definition for the C4 Model toolbox."""
from functools import partial

from gaphas.item import SE

from gaphor.C4Model import c4model, diagramitems
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import (
    DiagramType,
    DiagramTypes,
    ToolboxDefinition,
    ToolDef,
    ToolSection,
    default_namespace,
    general_tools,
    namespace_config,
    new_item_factory,
)
from gaphor.UML import diagramitems as uml_items
from gaphor.UML.actions.actionstoolbox import actions
from gaphor.UML.classes.classestoolbox import classes
from gaphor.UML.interactions.interactionstoolbox import interactions
from gaphor.UML.states.statestoolbox import states


def software_system_config(new_item):
    default_namespace(new_item)
    subject = new_item.subject
    subject.type = "Software System"
    subject.name = gettext("New Software System")


def container_config(new_item):
    default_namespace(new_item)
    subject = new_item.subject
    subject.type = "Container"
    subject.name = gettext("New Container")


def container_database_config(new_item):
    default_namespace(new_item)
    subject = new_item.subject
    subject.type = "Container"
    subject.technology = gettext("Database")
    subject.name = gettext("New Database")


def component_config(new_item):
    default_namespace(new_item)
    subject = new_item.subject
    subject.type = "Component"
    subject.name = gettext("New Component")


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
                config_func=partial(namespace_config, name=gettext("Person")),
            ),
            handle_index=SE,
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
            handle_index=SE,
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
            handle_index=SE,
        ),
        ToolDef(
            "c4-container-database",
            gettext("Container: Database"),
            "gaphor-c4-database-symbolic",
            "<Shift>B",
            new_item_factory(
                diagramitems.C4DatabaseItem,
                c4model.C4Database,
                config_func=container_database_config,
            ),
            handle_index=SE,
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
            handle_index=SE,
        ),
        ToolDef(
            "c4-dependency",
            gettext("Dependency"),
            "gaphor-dependency-symbolic",
            "d",
            new_item_factory(uml_items.DependencyItem),
            handle_index=0,
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

c4model_diagram_types: DiagramTypes = (
    DiagramType("c4", gettext("New C4 Diagram"), (c4,)),
    DiagramType("cls", gettext("New Class Diagram"), (classes,)),
    DiagramType("act", gettext("New Activity Diagram"), (actions,)),
    DiagramType("sd", gettext("New Sequence Diagram"), (interactions,)),
    DiagramType("stm", gettext("New State Machine Diagram"), (states,)),
)
