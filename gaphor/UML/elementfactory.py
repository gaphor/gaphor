"""Factory for and registration of model elements."""

import uuid
from contextlib import contextmanager


from gaphor.UML.diagram import Diagram
from gaphor.UML.element import Element, UnlinkEvent
from gaphor.UML.event import (
    ElementChangeEvent,
    ElementCreateEvent,
    ElementDeleteEvent,
    FlushFactoryEvent,
    ModelFactoryEvent,
)
from gaphor.core import inject
from gaphor.abc import Service
from gaphor.misc import odict


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

    def __init__(self, event_manager=None):
        self.event_manager = event_manager
        self._elements = odict.odict()
        self._observers = list()
        self._block_events = 0

    def shutdown(self):
        self.flush()

    def create(self, type):
        """
        Create a new model element of type ``type``.
        """
        obj = self.create_as(type, str(uuid.uuid1()))
        self.handle(ElementCreateEvent(self, obj))
        return obj

    def create_as(self, type, id):
        """
        Create a new model element of type 'type' with 'id' as its ID.
        This method should only be used when loading models, since it does
        not emit an ElementCreateEvent event.
        """
        assert issubclass(type, Element)
        obj = type(id, self)
        self._elements[id] = obj
        return obj

    def bind(self, element):
        """
        Bind an already created element to the element factory.
        The element may not be bound to another factory already.
        """
        if hasattr(element, "_model") and element._model:
            raise AttributeError("element is already bound")
        if self._elements.get(element.id):
            raise AttributeError("an element already exists with the same id")

        element._model = self
        self._elements[element.id] = element

    def size(self):
        """
        Return the amount of elements currently in the factory.
        """
        return len(self._elements)

    def lookup(self, id):
        """
        Find element with a specific id.
        """
        return self._elements.get(id)

    __getitem__ = lookup

    def __contains__(self, element):
        return self.lookup(element.id) is element

    def select(self, expression=None):
        """
        Iterate elements that comply with expression.
        """
        if expression is None:
            for e in self._elements.values():
                yield e
        else:
            for e in self._elements.values():
                if expression(e):
                    yield e

    def lselect(self, expression=None):
        """
        Like select(), but returns a list.
        """
        return list(self.select(expression))

    def keys(self):
        """
        Return a list with all id's in the factory.
        """
        return list(self._elements.keys())

    def iterkeys(self):
        """
        Return a iterator with all id's in the factory.
        """
        return iter(self._elements.keys())

    def values(self):
        """
        Return a list with all elements in the factory.
        """
        return list(self._elements.values())

    def itervalues(self):
        """
        Return a iterator with all elements in the factory.
        """
        return iter(self._elements.values())

    def is_empty(self):
        """
        Returns True if the factory holds no elements.
        """
        return bool(self._elements)

    def flush(self):
        """Flush all elements (remove them from the factory).

        Diagram elements are flushed first.  This is so that canvas updates
        are blocked.  The remaining elements are then flushed.
        """
        self.handle(FlushFactoryEvent(self))

        with self.block_events():
            for element in self.lselect(lambda e: isinstance(e, Diagram)):
                element.canvas.block_updates = True
                element.unlink()

            for element in self.lselect():
                element.unlink()

    def notify_model(self):
        """
        Send notification that a new model has been loaded by means of the
        ModelFactoryEvent event from gaphor.UML.event.
        """
        self.handle(ModelFactoryEvent(self))

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

    def handle(self, event):
        """
        Handle events coming from elements.
        """
        if type(event) is UnlinkEvent:
            self._unlink_element(event.element)
            event = ElementDeleteEvent(self, event.element)
        if self.event_manager and not self._block_events:
            self.event_manager.handle(event)

    def _unlink_element(self, element):
        """
        NOTE: Invoked from Element.unlink() to perform an element unlink.
        """
        try:
            del self._elements[element.id]
        except KeyError:
            pass
