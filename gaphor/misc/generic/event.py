""" Event management system.

This module provides API for event management. There are two APIs provided:

* Global event management API: subscribe, unsubscribe, handle.
* Local event management API: Manager

If you run only one instance of your application per Python
interpreter you can stick with global API, but if you want to have
more than one application instances running inside one interpreter and
to have different configurations for them -- you should use local API
and have one instance of Manager object per application instance.
"""

from typing import Callable, Set, Type, TypeVar

from gaphor.misc.generic.registry import Registry, TypeAxis


__all__ = "Manager"

Event = object
Handler = Callable[[object], None]
HandlerSet = Set[Handler]


class Manager:
    """ Event manager

    Provides API for subscribing for and firing events. There's also global
    event manager instantiated at module level with functions
    :func:`.subscribe`, :func:`.handle` and decorator :func:`.subscriber` aliased
    to corresponding methods of class.
    """

    def __init__(self) -> None:
        axes = (("event_type", TypeAxis()),)
        self.registry = Registry[HandlerSet, Event](*axes)

    def subscribe(self, handler: Handler, event_type: Type[Event]) -> None:
        """ Subscribe ``handler`` to specified ``event_type``"""
        handler_set = self.registry.get_registration(event_type)
        if handler_set is None:
            handler_set = self._register_handler_set(event_type)
        handler_set.add(handler)

    def unsubscribe(self, handler: Handler, event_type: Type[Event]) -> None:
        """ Unsubscribe ``handler`` from ``event_type``"""
        handler_set = self.registry.get_registration(event_type)
        if handler_set and handler in handler_set:
            handler_set.remove(handler)

    def handle(self, event: Event) -> None:
        """ Fire ``event``

        All subscribers will be executed with no determined order.
        """
        handler_sets = self.registry.query(event)
        for handler_set in handler_sets:
            if handler_set:
                for handler in set(handler_set):
                    handler(event)

    def _register_handler_set(self, event_type: Type[Event]) -> HandlerSet:
        """ Register new handler set for ``event_type``.
        """
        handler_set: HandlerSet = set()
        self.registry.register(handler_set, event_type)
        return handler_set

    def subscriber(self, event_type: Type[Event]) -> Callable[[Handler], Handler]:
        """ Decorator for subscribing handlers

        Works like this:

            >>> mymanager = Manager()
            >>> class MyEvent():
            ...     pass
            >>> @mymanager.subscriber(MyEvent)
            ... def mysubscriber(evt):
            ...     # handle event
            ...     return

            >>> mymanager.handle(MyEvent())

        """

        def registrator(func: Handler) -> Handler:
            self.subscribe(func, event_type)
            return func

        return registrator
