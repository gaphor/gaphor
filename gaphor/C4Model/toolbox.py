"""The action definition for the C4 Model toolbox."""

from functools import partial

from gaphas.item import SE

import gaphor.UML.uml as UML
from gaphor.C4Model import c4model, diagramitems
from gaphor.diagram.diagramtoolbox import (
    DiagramType,
    DiagramTypes,
    ElementCreateInfo,
    ToolboxDefinition,
    ToolDef,
    ToolSection,
    new_item_factory,
)
from gaphor.i18n import gettext, i18nize
from gaphor.UML.actions.actionstoolbox import actions
from gaphor.UML.classes.classestoolbox import classes
from gaphor.UML.general.generaltoolbox import general_tools
from gaphor.UML.interactions.interactionstoolbox import interactions
from gaphor.UML.states.statestoolbox import states
from gaphor.UML.toolboxconfig import default_namespace, namespace_config


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
                c4model.Person,
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
                c4model.Container,
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
                c4model.Container,
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
                c4model.Database,
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
                c4model.Container,
                config_func=component_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "c4-dependency",
            gettext("Dependency"),
            "gaphor-dependency-symbolic",
            "d",
            new_item_factory(diagramitems.C4DependencyItem),
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
    DiagramType(c4model.C4Diagram, i18nize("C4 Diagram"), (c4,)),
    DiagramType(UML.ClassDiagram, i18nize("Class Diagram"), (classes,)),
    DiagramType(UML.ActivityDiagram, i18nize("Activity Diagram"), (actions,)),
    DiagramType(UML.SequenceDiagram, i18nize("Sequence Diagram"), (interactions,)),
    DiagramType(UML.StateMachineDiagram, i18nize("State Machine Diagram"), (states,)),
    DiagramType(UML.Diagram, i18nize("Generic Diagram"), ()),
)

c4model_element_types = (
    ElementCreateInfo("package", i18nize("Package"), UML.Package, (UML.Package,)),
    ElementCreateInfo("activity", i18nize("Activity"), UML.Activity, (UML.Package,)),
    ElementCreateInfo(
        "interaction", i18nize("Interaction"), UML.Interaction, (UML.Package,)
    ),
    ElementCreateInfo(
        "statemachine", i18nize("State Machine"), UML.StateMachine, (UML.Package,)
    ),
    ElementCreateInfo("class", i18nize("Class"), UML.Class, (UML.Package,)),
    ElementCreateInfo("component", i18nize("Component"), UML.Component, (UML.Package,)),
    ElementCreateInfo("datatype", i18nize("Data Type"), UML.DataType, (UML.Package,)),
    ElementCreateInfo(
        "enumeration", i18nize("Enumeration"), UML.Enumeration, (UML.Package,)
    ),
    ElementCreateInfo(
        "primitive", i18nize("Primitive Type"), UML.PrimitiveType, (UML.Package,)
    ),
    ElementCreateInfo("person", i18nize("Person"), c4model.Person, (UML.Package,)),
    ElementCreateInfo(
        "database", i18nize("Database"), c4model.Database, (UML.Package,)
    ),
)
