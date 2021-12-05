#!/usr/bin/env python
"""Base class for model elements."""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Callable, Iterator, Protocol, TypeVar, overload

from gaphor.core.modeling.event import ElementUpdated
from gaphor.core.modeling.properties import (
    attribute,
    relation_many,
    relation_one,
    umlproperty,
)

if TYPE_CHECKING:
    from gaphor.core.modeling.coremodel import Comment
    from gaphor.core.modeling.diagram import Diagram
    from gaphor.core.modeling.presentation import Presentation

__all__ = ["Element"]

log = logging.getLogger(__name__)


class UnlinkEvent:
    """Used to tell event handlers this element should be unlinked."""

    def __init__(self, element: Element, diagram: Diagram | None = None):
        self.element = element
        self.diagram = diagram


Id = str


class Element:
    """Base class for all model data classes."""

    note: attribute[str] = attribute("note", str)
    appliedStereotype: relation_many[Element]
    comment: relation_many[Comment]
    directedRelationship: relation_many[Presentation]
    ownedElement: relation_many[Element]
    owner: relation_one[Element]
    presentation: relation_many[Presentation]
    relationship: relation_many[Presentation]
    ownedDiagram: relation_many[Diagram]

    def __init__(self, id: Id | None = None, model: RepositoryProtocol | None = None):
        """Create an element. As optional parameters an id and model can be
        given.

        Id is a serial number for the element. The default id is None and will
        result in an automatic creation of an id. An existing id (such as an
        int or string) can be provided as well.

        A model can be provided to refer to the model this element belongs to.
        """
        self._id: Id = id or str(uuid.uuid1())
        # The model this element belongs to.
        self._model = model
        self._unlink_lock = 0

    @property
    def id(self) -> Id:
        "Id"
        return self._id

    @property
    def model(self) -> RepositoryProtocol:
        """The owning model, raises AssertionError when model is not set."""
        assert (
            self._model
        ), "You can not retrieve the model since it's not set on construction"
        return self._model

    @classmethod
    def umlproperties(class_) -> Iterator[umlproperty]:
        """Iterate over all properties."""
        umlprop = umlproperty
        for propname in dir(class_):
            if not propname.startswith("_"):
                prop = getattr(class_, propname)
                if isinstance(prop, umlprop):
                    yield prop

    def save(self, save_func):
        """Save the state by calling save_func(name, value)."""
        for prop in self.umlproperties():
            prop.save(self, save_func)

    def load(self, name, value):
        """Loads value in name.

        Make sure that for every load postload() should be called.
        """
        prop = getattr(type(self), name)
        prop.load(self, value)

    def __str__(self):
        return f"<{self.__class__.__module__}.{self.__class__.__name__} element {self._id}>"

    __repr__ = __str__

    def postload(self):
        """Fix up the odds and ends."""
        for prop in self.umlproperties():
            prop.postload(self)

    def unlink(self):
        """Unlink the element. All the elements references are destroyed.

        The unlink lock is acquired while unlinking this elements
        properties to avoid recursion problems.
        """
        self.inner_unlink(UnlinkEvent(self))

    def inner_unlink(self, unlink_event):
        if self._unlink_lock:
            return

        try:
            self._unlink_lock += 1

            for prop in self.umlproperties():
                prop.unlink(self)

            log.debug("unlinking %s", self)
            self.handle(unlink_event)
            self._model = None
        finally:
            self._unlink_lock -= 1

    def handle(self, event):
        """Propagate incoming events."""
        model = self._model
        if model:
            model.handle(event)

    def watcher(self, default_handler: Handler | None = None) -> EventWatcherProtocol:
        model = self._model
        if model:
            return model.watcher(self, default_handler)
        else:
            return DummyEventWatcher()

    def isKindOf(self, class_: type[Element]) -> bool:
        """Returns true if the object is an instance of `class_`."""
        return isinstance(self, class_)

    def isTypeOf(self, other: Element) -> bool:
        """Returns true if the object is of the same type as other."""
        return isinstance(self, type(other))


class DummyEventWatcher:
    def watch(self, path: str, handler: Handler | None = None) -> DummyEventWatcher:
        return self

    def unsubscribe_all(self) -> None:
        pass


T = TypeVar("T", bound=Element)

Handler = Callable[[ElementUpdated], None]


class RepositoryProtocol(Protocol):
    def create(self, type: type[T]) -> T:
        ...

    def create_as(self, type: type[T], id: str) -> T:
        ...

    @overload
    def select(self, expression: Callable[[Element], bool]) -> Iterator[Element]:
        ...

    @overload
    def select(self, expression: type[T]) -> Iterator[T]:
        ...

    @overload
    def select(self, expression: None) -> Iterator[Element]:
        ...

    def lookup(self, id: str) -> Element | None:
        ...

    def watcher(
        self, element: Element, default_handler: Handler | None = None
    ) -> EventWatcherProtocol:
        ...

    def handle(self, event: object) -> None:
        ...


class EventWatcherProtocol(Protocol):
    def watch(self, path: str, handler: Handler | None = None) -> EventWatcherProtocol:
        ...

    def unsubscribe_all(self) -> None:
        ...
