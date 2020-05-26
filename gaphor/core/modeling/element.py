#!/usr/bin/env python
"""
Base class for model elements.
"""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Callable, Iterator, Optional, Type, TypeVar, Union

from typing_extensions import Protocol

from gaphor.core.modeling.event import ElementUpdated
from gaphor.core.modeling.properties import relation_many, relation_one, umlproperty

if TYPE_CHECKING:
    from gaphor.core.modeling.presentation import Presentation
    from gaphor.core.modeling.coremodel import Comment

__all__ = ["Element"]

log = logging.getLogger(__name__)


class UnlinkEvent:
    """Used to tell event handlers this element should be unlinked.
    """

    def __init__(self, element: Element):
        self.element = element


Id = Union[str, bool]


class Element:
    """
    Base class for all model data classes.
    """

    appliedStereotype: relation_many[Element]
    owner: relation_one[Element]
    ownedComment: relation_many[Comment]
    ownedElement: relation_many[Element]
    presentation: relation_many[Presentation]

    def __init__(
        self, id: Optional[Id] = None, model: Optional[RepositoryProtocol] = None
    ):
        """
        Create an element. As optional parameters an id and model can be
        given.

        Id is a serial number for the element. The default id is None and will
        result in an automatic creation of an id. An existing id (such as an
        int or string) can be provided as well. An id False will result in no
        id being  given (for "transient" or helper classes).

        A model can be provided to refer to the model this element belongs to.
        """
        super().__init__()
        self._id: Id = id or (id is not False and str(uuid.uuid1()) or False)
        # The model this element belongs to.
        self._model = model
        self._unlink_lock = 0

    @property
    def id(self) -> Id:
        "Id"
        return self._id

    @property
    def model(self) -> RepositoryProtocol:
        "The owning model, raises AssertionError when model is not set."
        assert (
            self._model
        ), "You can not retrieve the model since it's not set on construction"
        return self._model

    def umlproperties(self):
        """
        Iterate over all properties
        """
        umlprop = umlproperty
        class_ = type(self)
        for propname in dir(class_):
            if not propname.startswith("_"):
                prop = getattr(class_, propname)
                if isinstance(prop, umlprop):
                    yield prop

    def save(self, save_func):
        """
        Save the state by calling save_func(name, value).
        """
        for prop in self.umlproperties():
            prop.save(self, save_func)

    def load(self, name, value):
        """
        Loads value in name. Make sure that for every load postload()
        should be called.
        """
        try:
            prop = getattr(type(self), name)
        except AttributeError:
            log.exception(f"'{type(self).__name__}' has no property '{name}'")
        else:
            prop.load(self, value)

    def __str__(self):
        return f"<{self.__class__.__module__}.{self.__class__.__name__} element {self._id}>"

    __repr__ = __str__

    def postload(self):
        """
        Fix up the odds and ends.
        """
        for prop in self.umlproperties():
            prop.postload(self)

    def unlink(self):
        """
        Unlink the element. All the elements references are destroyed.

        The unlink lock is acquired while unlinking this elements properties
        to avoid recursion problems."""

        if self._unlink_lock:
            return

        try:
            self._unlink_lock += 1

            for prop in self.umlproperties():
                prop.unlink(self)

            self.handle(UnlinkEvent(self))
        finally:
            self._unlink_lock -= 1

    def handle(self, event):
        """
        Propagate incoming events
        """
        model = self._model
        if model:
            model.handle(event)

    def watcher(self, default_handler=None) -> EventWatcherProtocol:
        model = self._model
        if model:
            return model.watcher(self, default_handler)
        else:
            return DummyEventWatcher()

    # OCL methods: (from SMW by Ivan Porres (http://www.abo.fi/~iporres/smw))

    def isKindOf(self, class_: Type[Element]) -> bool:
        """
        Returns true if the object is an instance of `class_`.
        """
        return isinstance(self, class_)

    def isTypeOf(self, other: Element) -> bool:
        """
        Returns true if the object is of the same type as other.
        """
        return isinstance(self, type(other))


class DummyEventWatcher:
    def watch(self, path: str, handler: Optional[Handler] = None) -> DummyEventWatcher:
        return self

    def subscribe_all(self) -> None:
        pass

    def unsubscribe_all(self) -> None:
        pass


T = TypeVar("T", bound=Element)

Handler = Callable[[ElementUpdated], None]


class RepositoryProtocol(Protocol):
    def create(self, type: Type[T]) -> T:
        ...

    def create_as(self, type: Type[T], id: str) -> T:
        ...

    def select(
        self, expression: Union[Callable[[Element], bool], Type[T], None] = None
    ) -> Iterator[Element]:
        ...

    def watcher(
        self, element: Element, default_handler: Optional[Handler] = None
    ) -> EventWatcherProtocol:
        ...

    def handle(self, event: object) -> None:
        ...


class EventWatcherProtocol(Protocol):
    def watch(
        self, path: str, handler: Optional[Handler] = None
    ) -> EventWatcherProtocol:
        ...

    def subscribe_all(self) -> None:
        ...

    def unsubscribe_all(self) -> None:
        ...
