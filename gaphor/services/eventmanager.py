"""
Event Manager.
"""

from gaphor.abc import Service
from gaphor.misc.generic.event import Manager as _Manager


def event_handler(*event_types):
    """
    Mark a function/method as an event handler for a particular type of event.
    """

    def wrapper(func):
        func.__event_types__ = event_types
        return func

    return wrapper


class EventManager(Service):
    """
    The Event Manager.
    """

    def init(self, app):
        self._events = _Manager()

    def shutdown(self):
        pass

    def subscribe(self, handler):
        """
        Register a handler. Handlers are triggered (executed) when specific
        events are emitted through the handle() method.
        """
        event_types = getattr(handler, "__event_types__", None)
        if not event_types:
            raise Exception(f"No event types provided for function {handler}")

        for et in event_types:
            self._events.subscribe(handler, et)

    def unsubscribe(self, handler, event_types=None):
        """
        Unregister a previously registered handler.
        """
        event_types = getattr(handler, "__event_types__", None)
        if not event_types:
            raise Exception(f"No event types provided for function {handler}")

        for et in event_types:
            self._events.unsubscribe(handler, et)

    def handle(self, *events):
        """
        Send event notifications to registered handlers.
        """
        for e in events:
            self._events.handle(e)
