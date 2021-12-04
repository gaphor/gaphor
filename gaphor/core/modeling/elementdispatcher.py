""""""

from __future__ import annotations

import logging

from gaphor.abc import Service
from gaphor.core import event_handler
from gaphor.core.modeling.element import Element, Handler
from gaphor.core.modeling.event import (
    AssociationAdded,
    AssociationDeleted,
    AssociationSet,
    ElementUpdated,
    ModelReady,
)
from gaphor.core.modeling.properties import umlproperty

log = logging.getLogger(__name__)


class EventWatcher:
    """A helper for easy registering and unregistering event handlers."""

    def __init__(
        self,
        element: Element,
        element_dispatcher: ElementDispatcher | None,
        default_handler: Handler | None = None,
    ):
        self.element = element
        self.element_dispatcher = element_dispatcher
        self.default_handler: Handler | None = default_handler
        self._watched_paths: dict[str, Handler] = dict()

    def watch(self, path: str, handler: Handler | None = None) -> EventWatcher:
        """Watch a certain path of elements starting with the DiagramItem. The
        handler is optional and will default the default provided at
        construction time.

        Watches should be set in the constructor, so they can be registered
        and unregistered in one shot.

        This interface is fluent (returns self).
        """
        if handler:
            self._watched_paths[path] = handler
        elif self.default_handler:
            self._watched_paths[path] = self.default_handler
        else:
            raise ValueError("No handler provided for path " + path)

        dispatcher = self.element_dispatcher
        if dispatcher:
            dispatcher.subscribe(self._watched_paths[path], self.element, path)
        return self

    def unsubscribe_all(self, *_args):
        """Unregister handlers.

        Extra arguments are ignored (makes connecting to destroy signals
        much easier though).
        """
        dispatcher = self.element_dispatcher
        if not dispatcher:
            return

        for path, handler in self._watched_paths.items():
            dispatcher.unsubscribe(handler)


class ElementDispatcher(Service):
    """The Element based Dispatcher allows handlers to receive only events
    related to certain elements. Those elements should be registered too. A
    path should be provided, that is used to find those changes.

    The handlers are registered on their property attribute. This avoids
    subclass lookups and is pretty specific. As a result this dispatcher is
    tailored for dispatching events from the data model (ElementUpdated)

    For example: if you're a TransitionItem (gaphor.core.modeling.Presentation
    instance) and you're interested in the value of the guard attribute of the
    model element that's represented by this item (gaphor.UML.Transition), you
    can register a handler like this::

      dispatcher.subscribe(element,
              'guard.specification[LiteralSpecification].value', self._handler)

    Note the '[' and ']'. This is because guard references ValueSpecification,
    which does not have a value attribute. Therefore the default reference type
    is overruled in favour of the LiteralSpecification.

    This dispatcher keeps track of the kind of events that are dispatched. The
    dispatcher table is updated accordingly (so the right handlers are fired
    every time).
    """

    def __init__(self, event_manager, modeling_language):
        self.event_manager = event_manager
        self.modeling_language = modeling_language

        # Table used to fire events:
        # (event.element, event.property): { handler: set(path, ..), ..}
        self._handlers: dict[tuple[Element, umlproperty], dict[Handler, set]] = dict()

        # Fast resolution when handlers are disconnected
        # handler: [(element, property), ..]
        self._reverse: dict[Handler, list[tuple[Element, umlproperty]]] = dict()

        self.event_manager.subscribe(self.on_model_loaded)
        self.event_manager.subscribe(self.on_element_change_event)

    def shutdown(self) -> None:
        self.event_manager.unsubscribe(self.on_element_change_event)
        self.event_manager.unsubscribe(self.on_model_loaded)

    def subscribe(self, handler: Handler, element: Element, path: str) -> None:
        props = self._path_to_properties(element, path)
        self._add_handlers(element, props, handler)

    def unsubscribe(self, handler: Handler) -> None:
        """Unregister a handler from the registry."""
        try:
            reverse = reversed(self._reverse[handler])
        except KeyError:
            return

        for key in reverse:
            try:
                handlers = self._handlers[key]
            except KeyError:
                pass
            else:
                try:
                    del handlers[handler]
                except KeyError:
                    pass
                if not handlers:
                    del self._handlers[key]
        del self._reverse[handler]

    def _path_to_properties(self, element, path):
        """Given a start element and a path, return a tuple of properties
        (association, attribute, etc.) representing the path."""
        c = type(element)
        tpath = []
        for attr in path.split("."):
            cname = ""
            if "[" in attr:
                assert attr.endswith("]"), f'"{attr}" should end with "]"'
                attr, cname = attr[:-1].split("[")
            prop = getattr(c, attr)
            tpath.append(prop)

            if cname:
                c = self.modeling_language.lookup_element(cname)
                assert c and issubclass(
                    c, prop.type
                ), "{} should be a subclass of {}".format(c, prop.type)
            else:
                c = prop.type
        return tuple(tpath)

    def _add_handlers(self, element, props, handler):
        """Provided an element and a path of properties (props), register the
        handler for each property."""
        property, remainder = props[0], props[1:]
        key = (element, property)

        # Register key
        try:
            handlers = self._handlers[key]
        except KeyError:
            handlers = {}
            self._handlers[key] = handlers

        # Register handler and it's remaining paths
        try:
            remainders = handlers[handler]
        except KeyError:
            remainders = handlers[handler] = set()
        if remainder:
            remainders.add(remainder)

        # Also add them to the reverse table, easing disconnecting
        try:
            reverse = self._reverse[handler]
        except KeyError:
            reverse = []
            self._reverse[handler] = reverse

        reverse.append(key)

        # Apply remaining path
        if remainder:
            if property.upper == "*" or property.upper > 1:
                for e in property._get(element):
                    self._add_handlers(e, remainder, handler)
            else:
                e = property._get(element)
                if e and remainder:
                    self._add_handlers(e, remainder, handler)

    def _remove_handlers(self, element, property, handler):
        """Remove the handler of the path of elements."""
        key = element, property
        handlers = self._handlers.get(key)
        if not handlers:
            return

        if property.upper == "*" or property.upper > 1:
            for remainder in handlers.get(handler, ()):
                for e in property._get(element):
                    self._remove_handlers(e, remainder[0], handler)
        else:
            for remainder in handlers.get(handler, ()):
                e = property._get(element)
                if e:
                    self._remove_handlers(e, remainder[0], handler)
        try:
            del handlers[handler]
        except KeyError:
            log.debug(
                "Handler %s is not registered for %s.%s",
                handler,
                element,
                property,
                exc_info=True,
            )

        if not handlers:
            del self._handlers[key]

    @event_handler(ElementUpdated)
    def on_element_change_event(self, event):
        handlers = self._handlers.get((event.element, event.property))
        if handlers:
            try:
                for handler in set(handlers.keys()):
                    handler(event)
            finally:
                # Handle add/removal of handlers based on the kind of event
                # Filter out handlers that have no remaining properties
                if (
                    isinstance(event, (AssociationSet, AssociationDeleted))
                    and event.old_value
                ):
                    for handler, remainders in handlers.items():
                        for remainder in remainders:
                            self._remove_handlers(
                                event.old_value, remainder[0], handler
                            )

                if (
                    isinstance(event, (AssociationSet, AssociationAdded))
                    and event.new_value
                ):
                    for handler, remainders in handlers.items():
                        for remainder in remainders:
                            self._add_handlers(event.new_value, remainder, handler)

    @event_handler(ModelReady)
    def on_model_loaded(self, event):
        for key, value in list(self._handlers.items()):
            for h, remainders in list(value.items()):
                for remainder in remainders:
                    self._add_handlers(key[0], (key[1],) + remainder, h)
