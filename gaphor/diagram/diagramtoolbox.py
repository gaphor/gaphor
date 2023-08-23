"""This module contains the actions used in the Toolbox (lower left section of
the main window).

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
import getpass
import time
from abc import abstractmethod

from gaphas.item import SE

from gaphor.core import gettext
from gaphor.core.modeling import Comment, Diagram, Element, Presentation
from gaphor.diagram import general
from gaphor.diagram.group import group
from gaphor.diagram.support import (
    get_diagram_item,
    has_diagram_item,
    diagram_item_has_element,
)


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


class AbstractItemFactory:
    @abstractmethod
    def create_item(self, diagram, parent=None):
        """Creates item, configures the item and optionaly creates the element"""

    @abstractmethod
    def item_class(self, diagram):
        """Returns item class"""

    def subject_class(self):
        return None


class ItemOnlyFactory(AbstractItemFactory):
    def __init__(
        self, item_class: Type[Presentation], config_func: Optional[ConfigFuncType]
    ):
        assert not diagram_item_has_element(item_class)

        self._item_class = item_class
        self._config_func = config_func

    def create_item(self, diagram, parent=None):
        item = diagram.create(self.item_class(diagram), subject=None)

        if self._config_func:
            self._config_func(item)

        return item

    def item_class(self, diagram):
        return self._item_class


class ElementItemFactory(AbstractItemFactory):
    def __init__(
        self, subject_class: Type[Element], config_func: Optional[ConfigFuncType]
    ):
        assert has_diagram_item(subject_class)

        self._subject_class = subject_class
        self._config_func = config_func

    def create_item(self, diagram, parent=None):
        element_factory = diagram.model
        subject = element_factory.create(self._subject_class)

        item = diagram.create(self.item_class(diagram), subject=subject)

        if parent and group(parent.subject, item.subject):
            item.change_parent(parent)

        if self._config_func:
            self._config_func(item)

        return item

    def item_class(self, diagram):
        return get_diagram_item(self._subject_class, type(diagram))

    def subject_class(self):
        return self._subject_class


class DeferredElementItemFactory(ElementItemFactory):
    """Creates only item, but depending on the subject class"""

    def create_item(self, diagram, parent=None):
        item = diagram.create(self.item_class(diagram))

        if self._config_func:
            self._config_func(item)

        return item


def new_element_item_factory(
    subject_class: Type[Element], config_func: Optional[ConfigFuncType] = None
):
    """
    Creates new element and adds it on the diagram.
    ``config_func`` may be a function accepting the newly created item.
    """
    return ElementItemFactory(subject_class=subject_class, config_func=config_func)


def new_deferred_element_item_factory(
    subject_class: Type[Element], config_func: Optional[ConfigFuncType] = None
):
    """
    Creates new item depending on the diagram, but does not create the element.
    ``config_func`` may be a function accepting the newly created item.
    """
    return DeferredElementItemFactory(
        subject_class=subject_class, config_func=config_func
    )


def new_item_factory(
    item_class: Type[Presentation],
    config_func: Optional[ConfigFuncType] = None,
):
    """``config_func`` may be a function accepting the newly created item."""
    return ItemOnlyFactory(item_class=item_class, config_func=config_func)


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
            new_element_item_factory(Comment),
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
    ),
)
