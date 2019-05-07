"""
A registry for components (e.g. services) and event handling.
"""

from gaphor.abc import Service
from gaphor.application import ComponentLookupError
from gaphor.misc.generic.event import Manager


def event_handler(*event_types):
    """
    Mark a function/method as an event handler for a particular type of event.
    """

    def wrapper(func):
        func.__event_types__ = event_types
        return func

    return wrapper


class ComponentRegistry(Service):
    """
    The ComponentRegistry provides a home for application wide components.
    """

    def init(self, app):
        self._comp = set()
        self._events = Manager()

    def shutdown(self):
        pass

    def get_service(self, name):
        """Obtain a service used by Gaphor by name.
        E.g. service("element_factory")
        """
        return self.get(Service, name)

    def register(self, component, name):
        self._comp.add((component, name))

    def unregister(self, component):
        self._comp = {(c, n) for c, n in self._comp if not c is component}

    def get(self, base, name):
        found = {(c, n) for c, n in self._comp if isinstance(c, base) and n == name}
        if len(found) > 1:
            raise ComponentLookupError(
                f"More than one component matches {base}+{name}: {found}"
            )
        if len(found) == 0:
            raise ComponentLookupError(
                f"Component with type {base} and name {name} is not registered"
            )
        return next(iter(found))[0]

    def all(self, base):
        return ((c, n) for c, n in self._comp if isinstance(c, base))

    def register_handler(self, handler):
        """
        Register a handler. Handlers are triggered (executed) when specific
        events are emitted through the handle() method.
        """
        event_types = getattr(handler, "__event_types__", None)
        if not event_types:
            raise Exception(f"No event types provided for function {handler}")

        for et in event_types:
            self._events.subscribe(handler, et)

    def unregister_handler(self, handler=None, event_types=None):
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
            self._events.fire(e)
