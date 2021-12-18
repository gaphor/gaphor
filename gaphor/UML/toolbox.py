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
    DiagramType("act", gettext("Activity Diagram"), (actions,)),
    DiagramType("cls", gettext("Class Diagram"), (classes,)),
    DiagramType("cmp", gettext("Component Diagram"), (components,)),
    DiagramType("dep", gettext("Deployment diagram"), (components,)),
    DiagramType("pkg", gettext("Package Diagram"), (classes,)),
    DiagramType("prf", gettext("Profile Diagram"), (profiles,)),
    DiagramType("stm", gettext("State Machine Diagram"), (states,)),
    DiagramType("sd", gettext("Sequence Diagram"), (interactions,)),
    DiagramType("com", gettext("Communication Diagram"), (interactions,)),
    DiagramType("uc", gettext("Use Case Diagram"), (use_cases,)),
)
