"""This module contains the actions used in the Toolbox (lower left section of
the main window).

We bind the Toolbox to a diagram. When a diagram page (tab) is switched,
the actions bound to the toolbuttons should change as well.
"""

import getpass
import time
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
from gaphor.core.modeling import Comment, Diagram, Element, Picture, Presentation
from gaphor.diagram import general
from gaphor.diagram.group import group

ItemFactory = Callable[[Diagram, Optional[Presentation]], Presentation]
P = TypeVar("P", bound=Presentation, covariant=True)
ConfigFuncType = Callable[[P], None]


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


class DiagramType:
    id: str
    name: str
    sections: Collection[ToolSection]

    def __init__(self, id, name, sections):
        self.id = id
        self.name = name
        self.sections = sections

    def allowed(self, element: Type[Element]) -> bool:
        return True

    def create(self, element_factory, element):
        diagram = element_factory.create(Diagram)
        diagram.element = element
        diagram.name = diagram.gettext(self.name)
        diagram.diagramType = self.id

        return diagram


DiagramTypes = Sequence[DiagramType]


class ElementCreateInfo(NamedTuple):
    id: str
    name: str
    element_type: Type[Element]
    allowed_owning_elements: Collection[Type[Element]]


def tooliter(toolbox_actions: Sequence[Tuple[str, Sequence[ToolDef]]]):
    """Iterate toolbox items, regardless of section headers."""
    for _name, section in toolbox_actions:
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

        if parent and subject and group(parent.subject, item.subject):
            item.change_parent(parent)

        if config_func:
            config_func(item)

        return item

    item_factory.item_class = item_class  # type: ignore[attr-defined]
    item_factory.subject_class = subject_class  # type: ignore[attr-defined]
    return item_factory


def metadata_config(metadata_item: general.MetadataItem) -> None:
    metadata_item.createdBy = getpass.getuser()
    metadata_item.description = metadata_item.diagram.name
    metadata_item.revision = "1.0"
    metadata_item.createdOn = time.strftime("%Y-%m-%d")


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
        ToolDef(
            "toolbox-metadata",
            gettext("Diagram metadata"),
            "gaphor-metadata-symbolic",
            None,
            new_item_factory(general.MetadataItem, config_func=metadata_config),
        ),
        ToolDef(
            "toolbox-picture",
            gettext("Picture"),
            "gaphor-picture-symbolic",
            None,
            new_item_factory(general.PictureItem, Picture),
        ),
    ),
)
