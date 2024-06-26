#!/usr/bin/env python
"""Base class for model elements."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Callable, Iterator, Protocol, TypeVar, overload
from uuid import uuid1

from gaphor.core.modeling.collection import collection
from gaphor.core.modeling.event import ElementUpdated
from gaphor.core.modeling.properties import (
    attribute,
    relation_many,
    relation_one,
    umlproperty,
)

if TYPE_CHECKING:
    from gaphor.core.modeling.coremodel import (
        Comment,
        Dependency,
        Namespace,
        Relationship,
    )
    from gaphor.core.modeling.diagram import Diagram
    from gaphor.core.modeling.presentation import Presentation

__all__ = ["Element"]

log = logging.getLogger(__name__)


class UnlinkEvent:
    """Used to tell event handlers this element should be unlinked.

    This event is used internally and should not be handled outside
    `gaphor.core.modeling`.
    """

    def __init__(self, element: Element, diagram: Diagram | None = None):
        self.element = element
        self.diagram = diagram


Id = str


def uuid_generator():
    while True:
        yield str(uuid1())


_generator: Iterator[str] = uuid_generator()


def generate_id(generator=None):
    global _generator
    if generator:
        _generator = generator
    return next(_generator)


def self_and_owners(element: Element | None) -> Iterator[Element]:
    """Return the element and the ancestors (Element.owner)."""
    seen = set()
    e = element
    while e:
        if e in seen:
            return
        yield e
        seen.add(e)
        e = e.owner


class Element:
    """Base class for all model data classes."""

    name: attribute[str] = attribute("name", str)
    note: attribute[str] = attribute("note", str)
    comment: relation_many[Comment]
    ownedDiagram: relation_many[Diagram]
    ownedElement: relation_many[Element]
    owner: relation_one[Element]
    presentation: relation_many[Presentation]
    relationship: relation_many[Relationship]
    sourceRelationship: relation_many[Relationship]
    targetRelationship: relation_many[Relationship]
    clientDependency: relation_many[Dependency]
    supplierDependency: relation_many[Dependency]
    memberNamespace: relation_one[Namespace]
    namespace: relation_one[Namespace]

    # From UML:
    appliedStereotype: relation_many[Element]

    def __init__(self, id: Id | None = None, model: RepositoryProtocol | None = None):
        """Create an element. As optional parameters an id and model can be
        given.

        Id is a serial number for the element. The default id is None and will
        result in an automatic creation of an id. An existing id (such as an
        int or string) can be provided as well.

        A model can be provided to refer to the model this element belongs to.
        """
        self._id: Id = id or generate_id()
        # The model this element belongs to.
        # NOTE: Will be unset by ElementFactory once it's `unlink()`ed.
        self._model = model
        self._unlink_lock = 0

    @property
    def id(self) -> Id:
        "An id (read-only), unique within the model."
        return self._id

    @property
    def model(self) -> RepositoryProtocol:
        """The owning model, raises :class:`TypeError` when model is not set."""
        if not self._model:
            raise TypeError(
                "Can't retrieve the model since it's not set on construction"
            )
        return self._model

    @property
    def qualifiedName(self) -> list[str]:
        """Returns the qualified name of the element as a list."""
        qname = [e.name or "??" for e in self_and_owners(self)]
        qname.reverse()
        return qname

    @classmethod
    def umlproperties(cls) -> Iterator[umlproperty]:
        """Iterate over all properties."""
        umlprop = umlproperty
        for propname in dir(cls):
            if not propname.startswith("_"):
                prop = getattr(cls, propname)
                if isinstance(prop, umlprop):
                    yield prop

    def save(
        self,
        save_func: Callable[
            [str, str | bool | int | Element | collection[Element]], None
        ],
    ) -> None:
        """Save the state by calling ``save_func(name, value)``."""
        for prop in self.umlproperties():
            prop.save(self, save_func)  # type: ignore[arg-type]

    def load(
        self, name: str, value: str | bool | int | Element | collection[Element]
    ) -> None:
        """Loads value in name.

        Make sure that after all elements are loaded, postload() should be called.
        """
        prop = getattr(type(self), name)
        prop.load(self, value)

    def __str__(self):
        return f"<{self.__class__.__module__}.{self.__class__.__name__} element {self._id}>"

    __repr__ = __str__

    def postload(self) -> None:
        """Fix up the odds and ends.

        This is run after all elements are loaded.
        """
        for prop in self.umlproperties():
            prop.postload(self)

    def unlink(self) -> None:
        """Unlink the element.

        All the elements references are destroyed.
        For composite associations, the associated elements are also unlinked.

        The unlink lock is acquired while unlinking this element's
        properties to avoid recursion problems.
        """
        if self._unlink_lock:
            return

        self._unlink_lock += 1

        try:
            self.inner_unlink(UnlinkEvent(self))
        finally:
            self._unlink_lock -= 1

    def inner_unlink(self, unlink_event: UnlinkEvent):
        for prop in self.umlproperties():
            prop.unlink(self)

        log.debug("unlinking %s", self)
        self.handle(unlink_event)

    def handle(self, event) -> None:
        """Propagate incoming events.

        This only works if the element has been created by an :class:`~gaphor.core.modeling.ElementFactory`
        """
        if model := self._model:
            model.handle(event)

    def watcher(self, default_handler: Handler | None = None) -> EventWatcherProtocol:
        """Create a new watcher for this element.

        Watchers provide a convenient way to get signalled when a property relative to
        ``self`` has been changed.

        To use a watcher, the element should be created by a properly wired up :class:`~gaphor.core.modeling.ElementFactory``.

        This example is purely illustrative:

        >>> element = Element()
        >>> watcher = element.watcher(default_handler=print)
        >>> watcher.watch("note")  # Watch for changed on element.note
        """
        if model := self._model:
            return model.watcher(self, default_handler)
        return DummyEventWatcher()

    def isKindOf(self, class_: type[Element]) -> bool:
        """Returns :const:`True` if the object is an instance of ``class_``."""
        return isinstance(self, class_)

    def isTypeOf(self, other: Element) -> bool:
        """Returns :const:`True` if the object is of the same type as the ``other``."""
        return isinstance(self, type(other))

    def __setattr__(self, key, value):
        if key.startswith("_") or hasattr(self.__class__, key):
            super().__setattr__(key, value)
        else:
            raise AttributeError(
                f"Property {self.__class__.__name__}.{key} does not exist"
            )


class DummyEventWatcher:
    def watch(self, path: str, handler: Handler | None = None) -> DummyEventWatcher:
        return self

    def unsubscribe_all(self, *_args) -> None:
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
    def select(self, type_: type[T]) -> Iterator[T]:
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
