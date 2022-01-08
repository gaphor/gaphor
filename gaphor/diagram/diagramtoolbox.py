"""This module contains the actions used in the Toolbox (lower left section of
the main window.

We bind the Toolbox to a diagram. When a diagram page (tab) is switched,
the actions bound to the toolbuttons should change as well.
"""

from typing import (
    Callable,
    Collection,
    NamedTuple,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
)

from gaphas.item import SE

from gaphor.core import gettext
from gaphor.core.modeling import Comment, Diagram, Element, Presentation
from gaphor.diagram import general
from gaphor.diagram.grouping import Group
from gaphor.UML.recipes import owner_package

ItemFactory = Callable[[Diagram, Optional[Presentation]], Presentation]
P = TypeVar("P", bound=Presentation, covariant=True)
ConfigFuncType = Callable[[P], None]


def default_namespace(new_item):
    new_item.subject.package = owner_package(new_item.diagram)


def namespace_config(new_item, name=None):
    default_namespace(new_item)
    new_item.subject.name = gettext("New {name}").format(
        name=name or gettext(type(new_item.subject).__name__)
    )


class ToolDef(NamedTuple):
    id: str
    name: str
    icon_name: str
    shortcut: Optional[str]
    item_factory: Optional[ItemFactory]
    handle_index: int = -1


class ToolSection(NamedTuple):
    name: str
    tools: Collection[ToolDef]


ToolboxDefinition = Sequence[ToolSection]


class DiagramType(NamedTuple):
    id: str
    name: str
    sections: Collection[ToolSection]


DiagramTypes = Sequence[DiagramType]


def tooliter(toolbox_actions: Sequence[Tuple[str, Sequence[ToolDef]]]):
    """Iterate toolbox items, regardless of section headers."""
    for name, section in toolbox_actions:
        yield from section


def get_tool_def(modeling_language, tool_name):
    return next(
        t for t in tooliter(modeling_language.toolbox_definition) if t.id == tool_name
    )


def new_item_factory(
    item_class: Type[Presentation],
    subject_class: Optional[Type[Element]] = None,
    config_func: Optional[ConfigFuncType] = None,
):
    """``config_func`` may be a function accepting the newly created item."""

    def item_factory(diagram, parent=None):
        if subject_class:
            element_factory = diagram.model
            subject = element_factory.create(subject_class)
        else:
            subject = None

        item = diagram.create(item_class, subject=subject)

        adapter = Group(parent, item)
        if parent and adapter.can_contain():
            item.change_parent(parent)
            adapter.group()

        if config_func:
            config_func(item)

        return item

    item_factory.item_class = item_class  # type: ignore[attr-defined]
    return item_factory


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
            "toolbox-magnet",
            gettext("Magnet"),
            "gaphor-magnet-symbolic",
            "F1",
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
            new_item_factory(general.CommentItem, Comment),
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
