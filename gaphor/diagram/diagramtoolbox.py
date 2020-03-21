"""
This module contains the helpers used to create the actions used in the
Toolbox (lower left section of the main window). The actions are
defined in separate modules for each profile type (UML, SysML, etc).

The Toolbox is bound to a diagram. When a diagram page (tab) is
switched, the actions bound to the toolbuttons should change as well.
"""

from typing import Callable, NamedTuple, Optional, Sequence, Tuple

from gaphas.item import SE

from gaphor import UML, diagram
from gaphor.core import gettext
from gaphor.diagram.diagramtools import DefaultTool, PlacementTool
from gaphor.UML.event import DiagramItemCreated

__all__ = ["TOOLBOX_ACTIONS"]

ItemFactory = Callable[[UML.Diagram, Optional[UML.Presentation]], UML.Presentation]


class ToolDef(NamedTuple):
    id: str
    name: str
    icon_name: str
    shortcut: Optional[str]
    item_factory: Optional[ItemFactory]
    handle_index: int = -1


def namespace_config(new_item):
    subject = new_item.subject
    diagram = new_item.canvas.diagram
    subject.package = diagram.namespace
    subject.name = f"New{type(subject).__name__}"


def initial_pseudostate_config(new_item):
    new_item.subject.kind = "initial"


def history_pseudostate_config(new_item):
    new_item.subject.kind = "shallowHistory"


def metaclass_config(new_item):
    namespace_config(new_item)
    new_item.subject.name = "Class"
