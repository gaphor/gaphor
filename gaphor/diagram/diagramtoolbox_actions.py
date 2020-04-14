"""Provides the toolbox action definition for the profile requested."""

from typing import Sequence, Tuple

from gaphor.diagram.diagramtoolbox import ToolboxDefinition, ToolDef


def toolbox_actions(profile: str) -> ToolboxDefinition:
    """Get the toolbox actions from the profile name.

    Args:
        profile (String): The name of the profile selected.

    Returns (Set): The toolbox actions.

    """
    from gaphor.UML.modelprovider import UMLModelProvider
    from gaphor.SysML.modelprovider import SysMLModelProvider

    if profile == "UML":
        return UMLModelProvider().toolbox_definition
    elif profile == "SysML":
        return SysMLModelProvider().toolbox_definition
    else:
        return UMLModelProvider().toolbox_definition
