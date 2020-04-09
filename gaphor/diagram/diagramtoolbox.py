"""
This module contains the actions used in the Toolbox (lower left section
of the main window.

The Toolbox is bound to a diagram. When a diagram page (tab) is switched,
the actions bound to the toolbuttons should change as well.
"""

from typing import Callable, NamedTuple, Optional, Sequence, Tuple

from gaphas.item import SE

from gaphor import UML, diagram
from gaphor.core import gettext
from gaphor.core.modeling import Presentation
from gaphor.diagram.diagramtools import PlacementTool

ItemFactory = Callable[[UML.Diagram, Optional[Presentation]], Presentation]


class ToolDef(NamedTuple):
    id: str
    name: str
    icon_name: str
    shortcut: Optional[str]
    item_factory: Optional[ItemFactory]
    handle_index: int = -1
