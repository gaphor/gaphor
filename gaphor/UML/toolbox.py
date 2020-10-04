"""The action definition for the UML toolbox."""

from gaphor.diagram.diagramtoolbox import ToolboxDefinition, general_tools
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
