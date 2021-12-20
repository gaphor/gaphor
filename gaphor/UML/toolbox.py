"""The action definition for the UML toolbox."""

from gaphor.diagram.diagramtoolbox import (
    DiagramType,
    DiagramTypes,
    ToolboxDefinition,
    general_tools,
)
from gaphor.i18n import gettext
from gaphor.UML.actions.actionstoolbox import actions
from gaphor.UML.classes.classestoolbox import classes
from gaphor.UML.components.componentstoolbox import components
from gaphor.UML.interactions.interactionstoolbox import interactions
from gaphor.UML.profiles.profilestoolbox import profiles
from gaphor.UML.states.statestoolbox import states
from gaphor.UML.usecases.usecasetoolbox import use_cases

uml_toolbox_actions: ToolboxDefinition = (
    general_tools,
    classes,
    components,
    actions,
    interactions,
    states,
    use_cases,
    profiles,
)

uml_diagram_types: DiagramTypes = (
    DiagramType("cls", gettext("New Class Diagram"), (classes,)),
    DiagramType("pkg", gettext("New Package Diagram"), (classes,)),
    DiagramType("cmp", gettext("New Component Diagram"), (components,)),
    DiagramType("dep", gettext("New Deployment Diagram"), (components,)),
    DiagramType("act", gettext("New Activity Diagram"), (actions,)),
    DiagramType("sd", gettext("New Sequence Diagram"), (interactions,)),
    DiagramType("com", gettext("New Communication Diagram"), (interactions,)),
    DiagramType("stm", gettext("New State Machine Diagram"), (states,)),
    DiagramType("uc", gettext("New Use Case Diagram"), (use_cases,)),
    DiagramType("prf", gettext("New Profile Diagram"), (profiles,)),
)
