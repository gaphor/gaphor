# vim: sw=4
"""elementfactory.py
"""

import gaphor.misc.uniqueid as uniqueid
#import weakref
from element import Element
from diagram import Diagram

class ElementFactory(object):
    """The ElementFactory is used to create elements ans do lookups to
    elements. A model can contain only one Model element, though.

    Notifications are send with as arguments (name, element, *user_data).
    The following names are used:
    create - a new model element is created (element is newly created element)
    remove - a model element is removed (element is to be removed element)
    model - a new model has been loaded (element is None)
    flush - model is flushed: all element are removed from the factory
            (element is None)
    """
    def __init__ (self):
        self._elements = dict()
        self._observers = list()

    def create (self, type):
        """Create a new Model element of type type"""
        return self.create_as(type, uniqueid.generate_id())

    def create_as (self, type, id):
        """Create a new model element of type 'type' with 'id' as its ID.
        This method should only be used when loading models. If the ID is
        higher that the current id that should be used for the next item, the
        ID for the next item is set to id + 1."""
        assert issubclass(type, Element)
        obj = type(id)
        self._elements[id] = obj
        #obj.connect('__unlink__', self.__element_signal, weakref.ref(obj))
        obj.connect('__unlink__', self.__element_signal)
        self.notify(obj, 'create')
        return obj

    def lookup (self, id):
        try:
            return self._elements[id]
        except KeyError:
            return None

    def select(self, expression):
        """Create a list of elements that comply with expression."""
        l = []
        for e in self._elements.values():
            if expression(e):
                l.append(e)
        return l

    def keys (self):
        return self._elements.keys()

    def iterkeys (self):
        return self._elements.iterkeys()

    def values (self):
        return self._elements.values()

    def itervalues (self):
        return self._elements.itervalues()

    def is_empty(self):
        """Returns True if the factory holds no elements."""
        if self._elements:
            return False
        else:
            return True

    def flush(self):
        """Flush all elements (remove them from the factory)."""
        self.notify(None, 'flush')
        for key, value in self._elements.items():
            #print 'ElementFactory: unlinking', value
            #print 'references:', gc.get_referrers(value)
            if isinstance (value, Diagram):
                value.canvas.clear_undo()
                value.canvas.clear_redo()
            value.unlink()
        assert len(self._elements) == 0, 'Still items in the factory: %s' % str(self._elements.values())

    def connect(self, callback, *data):
        """Attach 'callback'."""
        self._observers.append((callback,) + data)

    def disconnect(self, callback, *data):
        """Detach a callback identified by it's data."""
        #print 'disconnect', callback, data
        cb = (callback,) + data
        # Remove all occurences of 'cb' from values
        # (if none is found ValueError is raised).
        try:
            while True:
                self._observers.remove(cb)
        except ValueError:
            pass

    def notify(self, element, name):
        """Send notification to attached callbacks that a property
        has changed. This is usually only called by the properties."""
        for cb_data in self._observers:
            try:
                apply(cb_data[0], (element, name) + cb_data[1:])
            except:
                pass

    def notify_model(self):
        self.notify(None, 'model')

    def __element_signal (self, element, pspec):
        """Remove an element from the factory """
        #element = weak_element()
        #if not element: return
	#log.debug('element %s send signal %s' % (element, name))
        if pspec == '__unlink__' and self._elements.has_key(element.id):
            log.debug('Unlinking element: %s' % element)
            del self._elements[element.id]
            self.notify(element, 'remove')
        elif pspec == '__relink__' and not self._elements.has_key(element.id):
            log.debug('Relinking element: %s' % element)
            self._elements[element.id] = element
            self.notify(element, 'create')

# Make one ElementFactory instance an application-wide resource
GaphorResource(ElementFactory)
