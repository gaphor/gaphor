""" Event management system.

This module provides API for event management. There are two APIs provided:

* Global event management API: subscribe, unsubscribe, fire.
* Local event management API: Manager

If you run only one instance of your application per Python
interpreter you can stick with global API, but if you want to have
more than one application instances running inside one interpreter and
to have different configurations for them -- you should use local API
and have one instance of Manager object per application instance.
"""

from collections import namedtuple

from .registry import Registry, TypeAxis

__all__ = ("Manager", "subscribe", "unsubscribe", "fire", "subscriber")


class HandlerSet(namedtuple("HandlerSet", ["parents", "handlers"])):
    """ Set of handlers for specific type of event.

    This object stores ``handlers`` for specific event type and
    ``parents`` reference to handler sets of event's supertypes.
    """

    @property
    def all_handlers(self):
        """ Iterate over own and supertypes' handlers.

        This iterator yields just unique values, so it won't yield the
        same handler twice, even if it was registered both for some
        event type and its supertype.
        """
        seen = set()
        seen_add = seen.add

        # yield own handlers first
        for handler in self.handlers:
            seen_add(handler)
            yield handler

        # yield supertypes' handlers then
        for parent in self.parents:
            for handler in parent.all_handlers:
                if not handler in seen:
                    seen_add(handler)
                    yield handler


class Manager(object):
    """ Event manager

    Provides API for subscribing for and firing events. There's also global
    event manager instantiated at module level with functions
    :func:`.subscribe`, :func:`.fire` and decorator :func:`.subscriber` aliased
    to corresponding methods of class.
    """

    def __init__(self):
        axes = (("event_type", TypeAxis()),)
        self.registry = Registry(*axes)

    def subscribe(self, handler, event_type):
        """ Subscribe ``handler`` to specified ``event_type``"""
        handler_set = self.registry.get_registration(event_type)
        if not handler_set:
            handler_set = self._register_handler_set(event_type)
        handler_set.handlers.add(handler)

    def unsubscribe(self, handler, event_type):
        """ Unsubscribe ``handler`` from ``event_type``"""
        handler_set = self.registry.get_registration(event_type)
        if handler_set and handler in handler_set.handlers:
            handler_set.handlers.remove(handler)

    def fire(self, event):
        """ Fire ``event``

        All subscribers will be executed with no determined order.
        """
        handler_set = self.registry.lookup(event)
        for handler in handler_set.all_handlers:
            handler(event)

    def _register_handler_set(self, event_type):
        """ Register new handler set for ``event_type``."""
        # Collect handler sets for supertypes
        parent_handler_sets = []
        parents = event_type.__bases__
        for parent in parents:
            parent_handlers = self.registry.get_registration(parent)
            if parent_handlers is None:
                parent_handlers = self._register_handler_set(parent)
            parent_handler_sets.append(parent_handlers)

        handler_set = HandlerSet(parents=parent_handler_sets, handlers=set())
        self.registry.register(handler_set, event_type)
        return handler_set

    def subscriber(self, event_type):
        """ Decorator for subscribing handlers

        Works like this:

            >>> mymanager = Manager()
            >>> class MyEvent():
            ...     pass
            >>> @mymanager.subscriber(MyEvent)
            ... def mysubscriber(evt):
            ...     # handle event
            ...     return

            >>> mymanager.fire(MyEvent())

        """

        def registrator(func):
            self.subscribe(func, event_type)
            return func

        return registrator


# Global event manager
_global_manager = Manager()

# Global event management API
subscribe = _global_manager.subscribe
unsubscribe = _global_manager.unsubscribe
fire = _global_manager.fire
subscriber = _global_manager.subscriber
