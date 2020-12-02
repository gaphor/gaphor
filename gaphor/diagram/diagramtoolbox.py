"""This module contains the actions used in the Toolbox (lower left section of
the main window.

We bind the Toolbox to a diagram. When a diagram page (tab) is switched,
the actions bound to the toolbuttons should change as well.
"""

from typing import Callable, NamedTuple, Optional, Sequence

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.core.modeling import Diagram, Presentation
from gaphor.diagram import general
from gaphor.diagram.diagramtools import new_item_factory

ItemFactory = Callable[[Diagram, Optional[Presentation]], Presentation]


def namespace_config(new_item):
    subject = new_item.subject
    diagram = new_item.diagram
    subject.package = diagram.namespace
    subject.name = f"New{type(subject).__name__}"


class ToolDef(NamedTuple):
    id: str
    name: str
    icon_name: str
    shortcut: Optional[str]
    item_factory: Optional[ItemFactory]
    handle_index: int = -1


class ToolSection(NamedTuple):
    name: str
    tools: Sequence[ToolDef]


ToolboxDefinition = Sequence[ToolSection]


general_tools = ToolSection(
    gettext("General"),
    (
        ToolDef(
            "toolbox-pointer",
            gettext("Pointer"),
            "gaphor-pointer-symbolic",
            "Escape",
            item_factory=None,
        ),
        ToolDef(
            "toolbox-line",
            gettext("Line"),
            "gaphor-line-symbolic",
            "l",
            new_item_factory(general.Line),
        ),
        ToolDef(
            "toolbox-box",
            gettext("Box"),
            "gaphor-box-symbolic",
            "b",
            new_item_factory(general.Box),
            SE,
        ),
        ToolDef(
            "toolbox-ellipse",
            gettext("Ellipse"),
            "gaphor-ellipse-symbolic",
            "e",
            new_item_factory(general.Ellipse),
            SE,
        ),
        ToolDef(
            "toolbox-comment",
            gettext("Comment"),
            "gaphor-comment-symbolic",
            "k",
            new_item_factory(general.CommentItem, UML.Comment),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-comment-line",
            gettext("Comment line"),
            "gaphor-comment-line-symbolic",
            "<Shift>K",
            new_item_factory(general.CommentLineItem),
        ),
    ),
)
