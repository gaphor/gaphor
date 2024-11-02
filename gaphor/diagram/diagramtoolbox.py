"""This module contains the actions used in the Toolbox (lower left section of
the main window).

We bind the Toolbox to a diagram. When a diagram page (tab) is switched,
the actions bound to the toolbuttons should change as well.
"""

from collections.abc import Callable, Collection, Sequence
from typing import (
    NamedTuple,
    TypeVar,
)

from gaphor.core.modeling import Diagram, Element, Presentation
from gaphor.diagram.group import group

ItemFactory = Callable[[Diagram, Presentation | None], Presentation]
P = TypeVar("P", bound=Presentation, covariant=True)
ConfigFuncType = Callable[[P], None]


class ToolDef(NamedTuple):
    id: str
    name: str
    icon_name: str
    shortcut: str | None
    item_factory: ItemFactory | None
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

    def allowed(self, element: type[Element]) -> bool:
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
    element_type: type[Element]
    allowed_owning_elements: Collection[type[Element]]


def tooliter(toolbox_actions: Sequence[tuple[str, Sequence[ToolDef]]]):
    """Iterate toolbox items, regardless of section headers."""
    for _name, section in toolbox_actions:
        yield from section


def get_tool_def(modeling_language, tool_name):
    return next(
        t for t in tooliter(modeling_language.toolbox_definition) if t.id == tool_name
    )


def new_item_factory(
    item_class: type[Presentation],
    subject_class: type[Element] | None = None,
    config_func: ConfigFuncType | None = None,
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
