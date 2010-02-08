# vim: sw=4
"""
Factory for and registration of model elements.
"""

from zope import interface
from zope import component
import uuid
from gaphor.misc import odict
from gaphor.interfaces import IService, IEventFilter
from gaphor.UML.interfaces import IElementCreateEvent, IElementDeleteEvent, \
                                  IFlushFactoryEvent, IModelFactoryEvent, \
                                  IElementChangeEvent, IElementEvent
from gaphor.UML.event import ElementCreateEvent, ElementDeleteEvent, \
                             FlushFactoryEvent, ModelFactoryEvent
from gaphor.UML.element import Element
from gaphor.UML.diagram import Diagram


class ElementChangedEventBlocker(object):
    """
    Blocks all events of type IElementChangeEvent.

    This filter is placed when the the element factory flushes it's content.
    """
    component.adapts(IElementChangeEvent)
    interface.implements(IEventFilter)

    def __init__(self, event):
        self._event = event

    def filter(self):
        """
        Return the event or None if the event is not to be emitted.
        """
        return 'Blocked by ElementFactory.flush()'


class ElementFactory(object):
    """
    The ElementFactory is used to create elements and do lookups to
    elements.

    Notifications are send with as arguments (name, element, *user_data).
    The following names are used:
    create - a new model element is created (element is newly created element)
    remove - a model element is removed (element is to be removed element)
    model - a new model has been loaded (element is None)
    flush - model is flushed: all element are removed from the factory
            (element is None)
    """
    interface.implements(IService)

    def __init__(self):
        self._elements = odict.odict()
        self._observers = list()
        self._app = None

    def init(self, app):
        self._app = app
        app.register_handler(self._element_deleted)

    def shutdown(self):
        # unregister after flush: the handler is needed to empty the _elements
        self.flush()
        if self._app:
            self._app.unregister_handler(self._element_deleted)

    def create(self, type):
        """
        Create a new model element of type ``type``.
        """
        obj = self.create_as(type, str(uuid.uuid1()))
        if self._app:
            self._app.handle(ElementCreateEvent(self, obj))
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
        if hasattr(element, '_factory') and element._factory:
            raise AttributeError, "element is already bound"
        if self._elements.get(element.id):
            raise AttributeError, "an element already exists with the same id"

        element._factory = self
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
            for e in self._elements.itervalues():
                yield e
        else:
            for e in self._elements.itervalues():
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
        return self._elements.keys()


    def iterkeys(self):
        """
        Return a iterator with all id's in the factory.
        """
        return self._elements.iterkeys()


    def values(self):
        """
        Return a list with all elements in the factory.
        """
        return self._elements.values()


    def itervalues(self):
        """
        Return a iterator with all elements in the factory.
        """
        return self._elements.itervalues()


    def is_empty(self):
        """
        Returns True if the factory holds no elements.
        """
        if self._elements:
            return False
        else:
            return True


    def flush(self):
        """
        Flush all elements (remove them from the factory).
        """
        app = self._app
        if app:
            app.handle(FlushFactoryEvent(self))
            app.register_subscription_adapter(ElementChangedEventBlocker)

        try:
            # First flush all diagrams:
            for value in list(self.select(lambda e: isinstance(e, Diagram))):
                # Make sure no updates happen while destroying the canvas
                value.canvas.block_updates = True
                value.unlink()
                if not app:
                    self._element_deleted(ElementDeleteEvent(self, value))
            for key, value in self._elements.items():
                value.unlink()
                if not app:
                    self._element_deleted(ElementDeleteEvent(self, value))
        finally:
            if app:
                app.unregister_subscription_adapter(ElementChangedEventBlocker)

        assert len(self._elements) == 0, 'Still items in the factory: %s' % str(self._elements.values())

        # Force Garbage collection, so memory allocated by items is freed.
        import gc
        for i in range(4): gc.collect()


    def swap_element(self, element, new_class):
	assert element in self._elements.values()
        if element.__class__ is not new_class:
            element.__class__ = new_class


    def notify_model(self):
        """
        Send notification that a new model has been loaded by means of the
        ModelFactoryEvent event from gaphor.UML.event.
        """
        if self._app:
            self._app.handle(ModelFactoryEvent(self))


    @component.adapter(IElementDeleteEvent)
    def _element_deleted(self, event):
        """
        Remove an element from the factory.
        """
        element = event.element
        try:
            del self._elements[element.id]
        except KeyError:
            pass


# vim:sw=4:et
