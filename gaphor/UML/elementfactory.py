"""Factory for and registration of model elements."""

import uuid
from collections import OrderedDict
from contextlib import contextmanager
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Type,
    TypeVar,
)

from gaphor.abc import Service
from gaphor.UML.diagram import Diagram
from gaphor.UML.element import Element, UnlinkEvent
from gaphor.UML.elementdispatcher import ElementDispatcher
from gaphor.UML.event import ElementCreated, ElementDeleted, ModelFlushed, ModelReady

if TYPE_CHECKING:
    from gaphor.services.eventmanager import EventManager  # noqa


T = TypeVar("T", bound=Element)


class ElementFactory(Service):
    """
    The ElementFactory is used to create elements and do lookups to
    elements.

    Notifications are sent as arguments (name, element, `*user_data`).
    The following names are used:
    create - a new model element is created (element is newly created element)
    remove - a model element is removed (element is to be removed element)
    model - a new model has been loaded (element is None) flush - model is
    flushed: all element are removed from the factory (element is None)
    """

    def __init__(self, event_manager: Optional["EventManager"] = None):
        self.event_manager = event_manager
        self.element_dispatcher = (
            ElementDispatcher(event_manager) if event_manager else None
        )
        self._elements: Dict[str, Element] = OrderedDict()
        self._block_events = 0

    def shutdown(self):
        self.flush()

    def create(self, type: Type[T]) -> T:
        """
        Create a new model element of type ``type``.
        """
        obj = self.create_as(type, str(uuid.uuid1()))
        self.handle(ElementCreated(self, obj))
        return obj

    def create_as(self, type: Type[T], id: str) -> T:
        """
        Create a new model element of type 'type' with 'id' as its ID.
        This method should only be used when loading models, since it does
        not emit an ElementCreated event.
        """
        assert issubclass(type, Element)
        obj = type(id, self)
        self._elements[id] = obj
        return obj

    def bind(self, element: Element) -> None:
        """
        Bind an already created element to the element factory.
        The element may not be bound to another factory already.
        """
        if hasattr(element, "_model") and element._model:
            raise AttributeError("element is already bound")
        if not isinstance(element.id, str):
            raise AttributeError(
                f"Element should contain a string id (found: {element.id}"
            )
        if self._elements.get(element.id):
            raise AttributeError("an element already exists with the same id")
        element._model = self
        self._elements[element.id] = element

    def size(self) -> int:
        """
        Return the amount of elements currently in the factory.
        """
        return len(self._elements)

    def lookup(self, id: str) -> Optional[Element]:
        """
        Find element with a specific id.
        """
        return self._elements.get(id)

    __getitem__ = lookup

    def __contains__(self, element: Element) -> bool:
        assert isinstance(element.id, str)
        return self.lookup(element.id) is element

    def select(
        self, expression: Optional[Callable[[Element], bool]] = None
    ) -> Iterator[Element]:
        """
        Iterate elements that comply with expression.
        """
        if expression is None:
            yield from self._elements.values()
        else:
            for e in self._elements.values():
                if expression(e):
                    yield e

    def lselect(
        self, expression: Optional[Callable[[Element], bool]] = None
    ) -> List[Element]:
        """
        Like select(), but returns a list.
        """
        return list(self.select(expression))

    def keys(self) -> List[str]:
        """
        Return a list with all id's in the factory.
        """
        return list(self._elements.keys())

    def iterkeys(self) -> Iterator[str]:
        """
        Return a iterator with all id's in the factory.
        """
        return iter(self._elements.keys())

    def values(self) -> List[Element]:
        """
        Return a list with all elements in the factory.
        """
        return list(self._elements.values())

    def itervalues(self) -> Iterator[Element]:
        """
        Return a iterator with all elements in the factory.
        """
        return iter(self._elements.values())

    def is_empty(self) -> bool:
        """
        Returns True if the factory holds no elements.
        """
        return bool(self._elements)

    def flush(self) -> None:
        """Flush all elements (remove them from the factory).

        Diagram elements are flushed first.  This is so that canvas updates
        are blocked.  The remaining elements are then flushed.
        """
        self.handle(ModelFlushed(self))

        with self.block_events():
            for element in self.lselect(lambda e: isinstance(e, Diagram)):
                assert isinstance(element, Diagram)
                element.canvas.block_updates = True
                element.unlink()

            for element in self.lselect():
                element.unlink()

    def model_ready(self) -> None:
        """
        Send notification that a new model has been loaded by means of the
        ModelReady event from gaphor.UML.event.
        """
        self.handle(ModelReady(self))

    @contextmanager
    def block_events(self):
        """
        Block events from being emitted.
        """
        self._block_events += 1

        try:
            yield self
        finally:
            self._block_events -= 1

    def handle(self, event: object) -> None:
        """
        Handle events coming from elements.
        """
        if isinstance(event, UnlinkEvent):
            self._unlink_element(event.element)
            event = ElementDeleted(self, event.element)
        if self.event_manager and not self._block_events:
            self.event_manager.handle(event)

    def _unlink_element(self, element: Element) -> None:
        """
        NOTE: Invoked from Element.unlink() to perform an element unlink.
        """
        try:
            assert isinstance(element.id, str)
            del self._elements[element.id]
        except KeyError:
            pass
