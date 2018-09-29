#!/usr/bin/env python
"""
Base class for UML model elements.
"""

__all__ = [ 'Element' ]

import threading
import uuid
from properties import umlproperty


class Element(object):
    """
    Base class for UML data classes.
    """

    def __init__(self, id=None, factory=None):
        """
        Create an element. As optional parameters an id and factory can be
        given.

        Id is a serial number for the element. The default id is None and will
        result in an automatic creation of an id. An existing id (such as an
        int or string) can be provided as well. An id False will result in no
        id being  given (for "transient" or helper classes).

        Factory can be provided to refer to the class that maintains the
        lifecycle of the element.
        """
        self._id = id or (id is not False and str(uuid.uuid1()) or False)
        # The factory this element belongs to.
        self._factory = factory
        self._unlink_lock = threading.Lock()


    id = property(lambda self: self._id, doc='Id')


    factory = property(lambda self: self._factory,
                       doc="The factory that created this element")


    def umlproperties(self):
        """
        Iterate over all UML properties 
        """
        umlprop = umlproperty
        class_ = type(self)
        for propname in dir(class_):
            if not propname.startswith('_'):
                prop = getattr(class_, propname)
                if isinstance(prop, umlprop):
                    yield prop


    def save(self, save_func):
        """
        Save the state by calling save_func(name, value).
        """
        for prop in self.umlproperties():
            prop.save(self, save_func)


    def load(self, name, value):
        """
        Loads value in name. Make sure that for every load postload()
        should be called.
        """
        try:
            prop = getattr(type(self), name)
        except AttributeError as e:
            raise AttributeError, "'%s' has no property '%s'" % \
                                        (type(self).__name__, name)
        else:
            prop.load(self, value)


    def postload(self):
        """
        Fix up the odds and ends.
        """
        for prop in self.umlproperties():
            prop.postload(self)


    def unlink(self):
        
        """Unlink the element. All the elements references are destroyed.
        
        The unlink lock is acquired while unlinking this elements properties
        to avoid recursion problems."""
        
        if self._unlink_lock.locked():
            
            return
        
        with self._unlink_lock:
            
            for prop in self.umlproperties():
                
                prop.unlink(self)
                
            if self._factory:
            
                self._factory._unlink_element(self)

    # OCL methods: (from SMW by Ivan Porres (http://www.abo.fi/~iporres/smw))

    def isKindOf(self, class_):
        """
        Returns true if the object is an instance of class_.
        """
        return isinstance(self, class_)


    def isTypeOf(self, other):
        """
        Returns true if the object is of the same type as other.
        """
        return isinstance(self, type(other))


    def __getstate__(self):
        d = dict(self.__dict__)
        try:
            del d['_factory']
        except KeyError:
            pass
        return d


    def __setstate__(self, state):
        self._factory = None
        self.__dict__.update(state)


try:
    import psyco
except ImportError:
    pass
else:
    psyco.bind(Element)

# vim:sw=4:et
