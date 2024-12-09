"""Factory for and registration of model elements."""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Protocol, TypeVar, overload

from gaphor.abc import Service
from gaphor.core.eventmanager import EventManager, event_handler
from gaphor.core.modeling.base import (
    Base,
    EventWatcherProtocol,
    Handler,
    Id,
    RepositoryProtocol,
    UnlinkEvent,
    generate_id,
)
from gaphor.core.modeling.diagram import Diagram
from gaphor.core.modeling.elementdispatcher import ElementDispatcher, EventWatcher
from gaphor.core.modeling.event import (
    ElementCreated,
    ElementDeleted,
    ModelFlushed,
)
from gaphor.core.modeling.presentation import Presentation

T = TypeVar("T", bound=Base)
P = TypeVar("P", bound=Presentation)


class EventHandler(Protocol):
    def handle(self, *events): ...


class RecordingEventManager:
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.events = []

    def handle(self, *events):
        self.events.extend(events)

    def replay(self):
        if self.event_manager:
            self.event_manager.handle(*self.events)


class ElementFactory(Service):
    """The ``ElementFactory`` is used as a central repository for a model.

    New model elements should be created by
    :obj:`~gaphor.core.modeling.ElementFactory.create`.

    Methods like :obj:`~gaphor.core.modeling.ElementFactory.select` can
    be used to find elements in the model.
    """

    def __init__(
        self,
        event_manager: EventManager | None = None,
        element_dispatcher: ElementDispatcher | None = None,
    ):
        self.event_manager: EventHandler | None = event_manager
        self.element_dispatcher = element_dispatcher
        self._elements: dict[Id, Base] = OrderedDict()
        if event_manager:
            event_manager.subscribe(self._on_unlink_event)

    def shutdown(self) -> None:
        self.flush()
        if isinstance(self.event_manager, EventManager):
            self.event_manager.unsubscribe(self._on_unlink_event)

    def create(self, type: type[T]) -> T:
        """Create a new model element of type ``type``.

        This method will only create model elements,
        not :obj:`~gaphor.core.modeling.Presentation` elements: those
        are created by :obj:`~gaphor.core.modeling.Diagram`.
        """
        return self.create_as(type, generate_id())

    def create_as(self, type: type[T], id: Id, diagram: Diagram | None = None) -> T:
        """Create a new model element of type 'type' with 'id' as its ID.

        This method should only be used when loading models, since it
        does not emit an ElementCreated event.
        """
        if id in self._elements:
            element = self._elements[id]
            if not isinstance(element, type):
                raise TypeError(
                    f"Element {element} already exists but has a different type {type}"
                )
            return element

        type_args: dict[str, Diagram | RepositoryProtocol]
        if issubclass(type, Presentation):
            if not diagram:
                raise TypeError("Presentation types require a diagram")
            type_args = {"diagram": diagram}
        elif issubclass(type, Base):
            if diagram:
                raise TypeError("Element types require no diagram")
            type_args = {"model": self}
        else:
            raise TypeError(f"Type {type} is not a valid model element")

        # Avoid events that reference this element before its created-event is emitted.
        event_recorder = RecordingEventManager(self.event_manager)
        with self.block_events(event_recorder):
            element = type(id=id, **type_args)  # type: ignore[arg-type]
        self._elements[id] = element
        self.handle(ElementCreated(self, element, diagram))
        event_recorder.replay()
        return element

    def size(self) -> int:
        """Return the amount of elements currently in the factory."""
        return len(self._elements)

    def lookup(self, id: Id) -> Base | None:
        """Find element with a specific id."""
        return self._elements.get(id)

    def __getitem__(self, id: Id) -> Base:
        return self._elements[id]

    def __iter__(self):
        return iter(self._elements.values())

    def __contains__(self, element: Base) -> bool:
        assert isinstance(element.id, Id)
        return self.lookup(element.id) is element

    @overload
    def select(self, expression: Callable[[Base], bool]) -> Iterator[Base]: ...

    @overload
    def select(self, expression: type[T]) -> Iterator[T]: ...

    @overload
    def select(self, expression: None) -> Iterator[Base]: ...

    def select(self, expression=None):
        """Iterate elements that comply with expression.

        Expressions can be:

        * :obj:`None`: return all elements.
        * A type: return all elements of that type, or subtypes.
        * An expression.
        """
        if expression is None:
            yield from self._elements.values()
        elif isinstance(expression, type):
            yield from (e for e in self._elements.values() if isinstance(e, expression))
        else:
            yield from (e for e in self._elements.values() if expression(e))

    def lselect(
        self, expression: Callable[[Base], bool] | type[T] | None = None
    ) -> list[Base]:
        """Like :obj:`~gaphor.core.modeling.ElementFactory.select`, but
        return a list, instead of an iterator.
        """
        return list(self.select(expression))

    def keys(self) -> Iterator[Id]:
        """Iterate all id's in the factory."""
        return iter(self._elements.keys())

    def values(self) -> Iterator[Base]:
        """Iterate all elements in the factory."""
        return iter(self._elements.values())

    def is_empty(self) -> bool:
        """Returns ``True`` if the factory holds no elements."""
        return bool(self._elements)

    def watcher(
        self, element: Base, default_handler: Handler | None = None
    ) -> EventWatcherProtocol:
        element_dispatcher = self.element_dispatcher
        return EventWatcher(element, element_dispatcher, default_handler)

    def flush(self) -> None:
        """Flush all elements (remove them from the factory).

        Diagram elements are flushed first. The remaining elements are
        flushed next.
        """
        with self.block_events():
            for element in self.lselect(Diagram):
                element.unlink()

            for element in self.lselect():
                element.unlink()

        self.handle(ModelFlushed(self))

    @contextmanager
    def block_events(self, new_event_manager: EventHandler | None = None):
        """Block events from being emitted.

        Instead, events are directed to `new_event_manager`, which
        defaults to a blocking event manager.
        """
        current_event_manager = self.event_manager
        self.event_manager = new_event_manager
        try:
            yield self
        finally:
            self.event_manager = current_event_manager

    def handle(self, event: object) -> None:
        """Handle events coming from elements."""
        if self.event_manager:
            self.event_manager.handle(event)
        elif isinstance(event, UnlinkEvent):
            self._on_unlink_event(event)

    @event_handler(UnlinkEvent)
    def _on_unlink_event(self, event):
        element = event.element
        element._model = None  # noqa: SLF001
        assert isinstance(element.id, Id)
        try:
            del self._elements[element.id]
        except KeyError:
            return
        if self.event_manager:
            self.event_manager.handle(
                ElementDeleted(self, event.element, event.diagram)
            )
