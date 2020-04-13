"""Provides the toolbox action definition for the profile requested."""

from typing import Sequence, Tuple

from gaphor.diagram.diagramtoolbox import ToolboxDefinition, ToolDef
from gaphor.diagram.diagramtoolbox_actions_sysml import sysml_toolbox_actions


def toolbox_actions(profile: str) -> ToolboxDefinition:
    """Get the toolbox actions from the profile name.

    Args:
        profile (String): The name of the profile selected.

    Returns (Set): The toolbox actions.

    """
    from gaphor.UML.modelprovider import UMLModelProvider

    if profile == "UML":
        return UMLModelProvider().toolbox_definition
    elif profile == "SysML":
        return sysml_toolbox_actions
    else:
        return UMLModelProvider().toolbox_definition
