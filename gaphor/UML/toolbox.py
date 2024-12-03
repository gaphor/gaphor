"""The action definition for the UML toolbox."""

from gaphor.diagram.diagramtoolbox import (
    DiagramType,
    DiagramTypes,
    ElementCreateInfo,
    ToolboxDefinition,
)
from gaphor.i18n import i18nize
from gaphor.UML.actions.actionstoolbox import actions
from gaphor.UML.classes.classestoolbox import classes
from gaphor.UML.deployments.deploymentstoolbox import deployments
from gaphor.UML.general.generaltoolbox import general_tools
from gaphor.UML.interactions.interactionstoolbox import interactions
from gaphor.UML.profiles.profilestoolbox import profiles
from gaphor.UML.states.statestoolbox import states
from gaphor.UML.uml import (
    Activity,
    Actor,
    Artifact,
    Class,
    Component,
    DataType,
    Device,
    Enumeration,
    InstanceSpecification,
    Interaction,
    Interface,
    Node,
    Package,
    Profile,
    StateMachine,
    Stereotype,
    UseCase,
)
from gaphor.UML.usecases.usecasetoolbox import use_cases

uml_toolbox_actions: ToolboxDefinition = (
    general_tools,
    classes,
    deployments,
    actions,
    interactions,
    states,
    use_cases,
    profiles,
)

uml_diagram_types: DiagramTypes = (
    DiagramType("cls", i18nize("Class Diagram"), (classes,)),
    DiagramType("pkg", i18nize("Package Diagram"), (classes,)),
    DiagramType("cmp", i18nize("Component Diagram"), (classes,)),
    DiagramType("dep", i18nize("Deployment Diagram"), (deployments,)),
    DiagramType("act", i18nize("Activity Diagram"), (actions,)),
    DiagramType("sd", i18nize("Sequence Diagram"), (interactions,)),
    DiagramType("com", i18nize("Communication Diagram"), (interactions,)),
    DiagramType("stm", i18nize("State Machine Diagram"), (states,)),
    DiagramType("uc", i18nize("Use Case Diagram"), (use_cases,)),
    DiagramType("prf", i18nize("Profile Diagram"), (profiles,)),
)

uml_element_types = (
    ElementCreateInfo("activity", i18nize("Activity"), Activity, (Package,)),
    ElementCreateInfo("actor", i18nize("Actor"), Actor, (Package,)),
    ElementCreateInfo("artifact", i18nize("Artifact"), Artifact, (Package,)),
    ElementCreateInfo("class", i18nize("Class"), Class, (Package,)),
    ElementCreateInfo("component", i18nize("Component"), Component, (Package,)),
    ElementCreateInfo("datatype", i18nize("Data Type"), DataType, (Package,)),
    ElementCreateInfo("device", i18nize("Device"), Device, (Package,)),
    ElementCreateInfo("enumeration", i18nize("Enumeration"), Enumeration, (Package,)),
    ElementCreateInfo(
        "instancespecification",
        i18nize("Instance Specification"),
        InstanceSpecification,
        (Package,),
    ),
    ElementCreateInfo("interaction", i18nize("Interaction"), Interaction, (Package,)),
    ElementCreateInfo("interface", i18nize("Interface"), Interface, (Package,)),
    ElementCreateInfo("node", i18nize("Node"), Node, (Package,)),
    ElementCreateInfo("profile", i18nize("Profile"), Profile, (Package,)),
    ElementCreateInfo(
        "statemachine", i18nize("State Machine"), StateMachine, (Package,)
    ),
    ElementCreateInfo("stereotype", i18nize("Stereotype"), Stereotype, (Package,)),
    ElementCreateInfo("usecase", i18nize("Use Case"), UseCase, (Package,)),
)
