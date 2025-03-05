"""Event Manager."""

import asyncio
import inspect
from collections import deque

from generic.event import Event, Handler
from generic.event import Manager as _Manager

from gaphor.abc import Service


def event_handler(*event_types):
    """Mark a function/method as an event handler for a particular type of
    event.

    Given a custom event type:

    >>> class CustomEvent:
    ...     def __str__(self):
    ...         return type(self).__name__

    You can apply this to a handler method or function:

    >>> @event_handler(CustomEvent)
    ... def custom_handler(event: CustomEvent):
    ...     print(event)

    This will allow you to let the even be handled by an event manager:

    >>> event_manager = EventManager()
    >>> event_manager.subscribe(custom_handler)
    >>> event_manager.handle(CustomEvent())
    CustomEvent
    """

    def wrapper(func):
        func.__event_types__ = event_types
        return func

    return wrapper


class EventManager(Service):
    """The Event Manager provides a flexible way to dispatch events.

    Event dispatching is a central component in Gaphor. It allows components
    in Gaphor to react to changes in the application.

    Events are dispatched by type.
    """

    def __init__(self) -> None:
        self._events = _Manager()
        self._priority = _Manager()
        self._queue: deque[Event] = deque()
        self._async_tasks: set[asyncio.Task] = set()
        self._handling = False

    def shutdown(self) -> None:
        for task in set(self._async_tasks):
            task.cancel()

    def subscribe(self, handler: Handler) -> None:
        """Register a handler.

        Handlers are triggered (executed) when events are
        emitted through the :obj:`~gaphor.core.eventmanager.EventManager.handle` method.
        """
        if inspect.iscoroutinefunction(handler):

            def async_handler(event: Event) -> None:
                coro = handler(event)
                task = asyncio.create_task(coro)
                self._async_tasks.add(task)
                task.add_done_callback(self._task_done)

            self._subscribe(
                self._events, async_handler, getattr(handler, "__event_types__", None)
            )
        else:
            self._subscribe(self._events, handler)

    async def gather_tasks(self):
        if self._async_tasks:
            await asyncio.gather(*self._async_tasks)

    def _task_done(self, task: asyncio.Task) -> None:
        self._async_tasks.remove(task)

    def priority_subscribe(self, handler: Handler) -> None:
        """Register a handler.

        Priority handlers are executed directly. They should not raise
        other events, cause that can cause a problem in the exection order.

        It's basically to make sure that all events are recorded by the
        undo manager.
        """
        self._subscribe(self._priority, handler)

    def _subscribe(self, manager: _Manager, handler: Handler, event_types=None) -> None:
        event_types = getattr(handler, "__event_types__", event_types)
        if not event_types:
            raise Exception(f"No event types provided for function {handler}")

        for et in event_types:
            manager.subscribe(handler, et)

    def unsubscribe(self, handler: Handler) -> None:
        """Unregister a previously registered handler."""
        event_types = getattr(handler, "__event_types__", None)
        if not event_types:
            raise Exception(f"No event types provided for function {handler}")

        for et in event_types:
            self._priority.unsubscribe(handler, et)
            self._events.unsubscribe(handler, et)

    def handle(self, *events: Event) -> None:
        """Send event notifications to registered handlers."""
        queue = self._queue
        queue.extendleft(events)

        for event in events:
            self._priority.handle(event)

        if not self._handling:
            self._handling = True
            try:
                while queue:
                    self._events.handle(queue.pop())
            finally:
                self._handling = False
