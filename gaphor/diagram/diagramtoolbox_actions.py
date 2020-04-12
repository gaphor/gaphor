"""Provides the toolbox action definition for the profile requested."""

from typing import Sequence, Tuple

from gaphor.diagram.diagramtoolbox import ToolDef
from gaphor.diagram.diagramtoolbox_actions_sysml import sysml_toolbox_actions
from gaphor.UML.toolbox import uml_toolbox_actions


def toolbox_actions(profile: str) -> Sequence[Tuple[str, Sequence[ToolDef]]]:
    """Get the toolbox actions from the profile name.

    Args:
        profile (String): The name of the profile selected.

    Returns (Set): The toolbox actions.

    """
    if profile == "UML":
        return uml_toolbox_actions
    elif profile == "SysML":
        return sysml_toolbox_actions
    else:
        return uml_toolbox_actions
