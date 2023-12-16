"""The action definition for the C4 Model toolbox."""
from functools import partial

from gaphas.item import SE

from gaphor.C4Model import c4model, diagramitems
from gaphor.diagram.diagramtoolbox import (
    DiagramType,
    DiagramTypes,
    ElementCreateInfo,
    ToolboxDefinition,
    ToolDef,
    ToolSection,
    general_tools,
    new_item_factory,
)
from gaphor.i18n import gettext, i18nize
from gaphor.UML import diagramitems as uml_items
from gaphor.UML.actions.actionstoolbox import actions
from gaphor.UML.classes.classestoolbox import classes
from gaphor.UML.interactions.interactionstoolbox import interactions
from gaphor.UML.states.statestoolbox import states
from gaphor.UML.toolboxconfig import default_namespace, namespace_config
from gaphor.UML.uml import (
    Activity,
    Class,
    Component,
    DataType,
    Enumeration,
    Interaction,
    Package,
    PrimitiveType,
    StateMachine,
)


def software_system_config(new_item):
    default_namespace(new_item)
    subject = new_item.subject
    subject.type = "Software System"
    subject.name = new_item.diagram.gettext("New Software System")


def container_config(new_item):
    default_namespace(new_item)
    subject = new_item.subject
    subject.type = "Container"
    subject.name = new_item.diagram.gettext("New Container")


def container_database_config(new_item):
    default_namespace(new_item)
    subject = new_item.subject
    subject.type = "Container"
    subject.technology = new_item.diagram.gettext("Database")
    subject.name = new_item.diagram.gettext("New Database")


def component_config(new_item):
    default_namespace(new_item)
    subject = new_item.subject
    subject.type = "Component"
    subject.name = new_item.diagram.gettext("New Component")


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
                config_func=partial(namespace_config, name=i18nize("Person")),
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
            "u",
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
    DiagramType("c4", i18nize("New C4 Diagram"), (c4,)),
    DiagramType("cls", i18nize("New Class Diagram"), (classes,)),
    DiagramType("act", i18nize("New Activity Diagram"), (actions,)),
    DiagramType("sd", i18nize("New Sequence Diagram"), (interactions,)),
    DiagramType("stm", i18nize("New State Machine Diagram"), (states,)),
)

c4model_element_types = (
    ElementCreateInfo("activity", i18nize("New Activity"), Activity, (Package,)),
    ElementCreateInfo(
        "interaction", i18nize("New Interaction"), Interaction, (Package,)
    ),
    ElementCreateInfo(
        "statemachine", i18nize("New State Machine"), StateMachine, (Package,)
    ),
    ElementCreateInfo("class", i18nize("New Class"), Class, (Package,)),
    ElementCreateInfo("component", i18nize("New Component"), Component, (Package,)),
    ElementCreateInfo("datatype", i18nize("New Data Type"), DataType, (Package,)),
    ElementCreateInfo(
        "enumeration", i18nize("New Enumeration"), Enumeration, (Package,)
    ),
    ElementCreateInfo(
        "primitive", i18nize("New Primitive Type"), PrimitiveType, (Package,)
    ),
    ElementCreateInfo("person", i18nize("New Person"), c4model.C4Person, (Package,)),
    ElementCreateInfo(
        "database", i18nize("New Database"), c4model.C4Database, (Package,)
    ),
)
