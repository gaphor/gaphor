"""The action definition for the UML toolbox."""

import gaphor.UML.uml as UML
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
    DiagramType(UML.ClassDiagram, i18nize("Class Diagram"), (classes,)),
    DiagramType(UML.PackageDiagram, i18nize("Package Diagram"), (classes,)),
    DiagramType(UML.ComponentDiagram, i18nize("Component Diagram"), (classes,)),
    DiagramType(UML.DeploymentDiagram, i18nize("Deployment Diagram"), (deployments,)),
    DiagramType(UML.ActivityDiagram, i18nize("Activity Diagram"), (actions,)),
    DiagramType(UML.SequenceDiagram, i18nize("Sequence Diagram"), (interactions,)),
    DiagramType(
        UML.CommunicationDiagram, i18nize("Communication Diagram"), (interactions,)
    ),
    DiagramType(UML.StateMachineDiagram, i18nize("State Machine Diagram"), (states,)),
    DiagramType(UML.UseCaseDiagram, i18nize("Use Case Diagram"), (use_cases,)),
    DiagramType(UML.ProfileDiagram, i18nize("Profile Diagram"), (profiles,)),
    DiagramType(UML.Diagram, i18nize("Generic Diagram"), ()),
)

uml_element_types = (
    ElementCreateInfo("package", i18nize("Package"), UML.Package, (UML.Package,)),
    ElementCreateInfo("activity", i18nize("Activity"), UML.Activity, (UML.Package,)),
    ElementCreateInfo("actor", i18nize("Actor"), UML.Actor, (UML.Package,)),
    ElementCreateInfo("artifact", i18nize("Artifact"), UML.Artifact, (UML.Package,)),
    ElementCreateInfo("class", i18nize("Class"), UML.Class, (UML.Package,)),
    ElementCreateInfo("component", i18nize("Component"), UML.Component, (UML.Package,)),
    ElementCreateInfo("datatype", i18nize("Data Type"), UML.DataType, (UML.Package,)),
    ElementCreateInfo("device", i18nize("Device"), UML.Device, (UML.Package,)),
    ElementCreateInfo(
        "enumeration", i18nize("Enumeration"), UML.Enumeration, (UML.Package,)
    ),
    ElementCreateInfo(
        "instancespecification",
        i18nize("Instance Specification"),
        UML.InstanceSpecification,
        (UML.Package,),
    ),
    ElementCreateInfo(
        "interaction", i18nize("Interaction"), UML.Interaction, (UML.Package,)
    ),
    ElementCreateInfo("interface", i18nize("Interface"), UML.Interface, (UML.Package,)),
    ElementCreateInfo("node", i18nize("Node"), UML.Node, (UML.Package,)),
    ElementCreateInfo("profile", i18nize("Profile"), UML.Profile, (UML.Package,)),
    ElementCreateInfo(
        "statemachine", i18nize("State Machine"), UML.StateMachine, (UML.Package,)
    ),
    ElementCreateInfo(
        "stereotype", i18nize("Stereotype"), UML.Stereotype, (UML.Package,)
    ),
    ElementCreateInfo("usecase", i18nize("Use Case"), UML.UseCase, (UML.Package,)),
)
