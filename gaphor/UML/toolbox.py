"""The action definition for the UML toolbox."""

from gaphor.diagram.diagramtoolbox import (
    DiagramType,
    DiagramTypes,
    ToolboxDefinition,
    general_tools,
)
from gaphor.i18n import i18nize
from gaphor.UML.actions.actionstoolbox import actions
from gaphor.UML.classes.classestoolbox import classes
from gaphor.UML.deployments.deploymentstoolbox import deployments
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
    DiagramType("cls", i18nize("New Class Diagram"), (classes,)),
    DiagramType("pkg", i18nize("New Package Diagram"), (classes,)),
    DiagramType("cmp", i18nize("New Component Diagram"), (classes,)),
    DiagramType("dep", i18nize("New Deployment Diagram"), (deployments,)),
    DiagramType("act", i18nize("New Activity Diagram"), (actions,)),
    DiagramType("sd", i18nize("New Sequence Diagram"), (interactions,)),
    DiagramType("com", i18nize("New Communication Diagram"), (interactions,)),
    DiagramType("stm", i18nize("New State Machine Diagram"), (states,)),
    DiagramType("uc", i18nize("New Use Case Diagram"), (use_cases,)),
    DiagramType("prf", i18nize("New Profile Diagram"), (profiles,)),
)
