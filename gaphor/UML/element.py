#!/usr/bin/env python
# vim:sw=4:et
"""Element:

Method names have changed on some places to emphasize that we deal
with a completely new data model here.

save()/load()/postload()
    Load/save the element.

unlink()
     Remove all references to the element. This is done by emiting the
     '__unlink__' signal to all attached signals. unlink() can not be called
     recursively.
relink()
    Inverse operation of unlink(). Used by diagram items during undo operations.

connect ('name', callback, *data) or
connect (('name', 'other_property'), callback, *data)
    Connect 'callback' to recieve notifications if one of the properties
    change (the latter being more memory efficient if you want to listen on
    more properties). The listener will recieve the property name as
    first argument, followed by *data.

disconnect (callback, *data)
    Disconnect callback as listener.

notify (name)
    Notify all listeners the property 'name' has changed.
    The notifier calls callbacks registered by connect() by sending
    callback(self, pspec, *data)
    where self is the data object (Element) and pspec is the property spec.
"""

__all__ = [ 'Element' ]

import types, mutex
import gaphor.misc.uniqueid as uniqueid
from properties import umlproperty, association

class Element(object):
    """Base class for UML data classes."""

    def __init__(self, id=None):
        self.id = id or uniqueid.generate_id()
        self._observers = dict()
        self.__in_unlink = mutex.mutex()

    def save(self, save_func):
        """Save the state by calling save_func(name, value)."""
        umlprop = umlproperty
        clazz = type(self)
        for propname in dir(clazz):
            prop = getattr(clazz, propname)
            if isinstance(prop, umlprop):
                prop.save(self, save_func)

    def load(self, name, value):
        """Loads value in name. Make sure that for every load postload()
        should be called.
        """
        try:
            prop = getattr(type(self), name)
        except AttributeError, e:
            raise AttributeError, "'%s' has no property '%s'" % \
                                        (type(self).__name__, name)
        else:
            prop.load(self, value)

    def postload(self):
        """Fix up the odds and ends.
        """
        for name in dir(type(self)):
            try:
                prop = getattr(type(self), name)
            except AttributeError, e:
                raise AttributeError, "'%s' has no property '%s'" % \
                                            (type(self).__name__, name)
            else:
                if isinstance(prop, umlproperty):
                    prop.postload(self)

    def __unlink(self, signal):
        """Unlink the element. For both the __unlink__ and __relink__ signal
        the __unlink__ callback list is used.
        """
        # Uses a mutex to make sure it is not called recursively
        if self.__in_unlink.testandset():
            try:
                self.notify(signal, '__unlink__')
            finally:
                self.__in_unlink.unlock()

    def unlink(self):
        """Unlink the element."""
        log.debug('Element.unlink(%s)' % self)
        self.__unlink('__unlink__')

    def relink(self):
        """Undo the unlink operation."""
        log.debug('Element.relink(%s)' % self)
        self.__unlink('__relink__')

    def connect(self, names, callback, *data):
        """Attach 'callback' to a list of names. Names may also be a string.
        A name is the name od a property of the object or '__unlink__'.
        """
        #log.debug('Element.connect(%s, %s, %s)' % (names, callback, data))
        if type(names) is types.StringType:
            names = (names,)
        cb = (callback,) + data
        for name in names:
            try:
                o = self._observers[name]
                if not cb in o:
                    o.append(cb)
            except KeyError:
                # create new entry
                self._observers[name] = [cb]

    def disconnect(self, callback, *data):
        """Detach a callback identified by it's data."""
        cb = (callback,) + data
        for values in self._observers.values():
            # Remove all occurences of 'cb' from values
            # (if none is found ValueError is raised).
            try:
                while True:
                    values.remove(cb)
            except ValueError:
                pass

    def notify(self, name, cb_name=None):
        """Send notification to attached callbacks that a property
        has changed. the __relink__ signal uses the callbacks for __unlink__.
        """
        cb_list = self._observers.get(cb_name or name, ())
        #log.debug('Element.notify: %s' % cb_list)
        try:
            pspec = getattr(type(self), name)
        except AttributeError:
            pspec = name
        
        # Use a copy of the list to ensure all items are notified
        for cb_data in list(cb_list):
            try:
                apply(cb_data[0], (self, pspec) + cb_data[1:])
            except:
                import traceback
                traceback.print_exc()

    # OCL methods: (from SMW by Ivan Porres (http://www.abo.fi/~iporres/smw))

    def isKindOf(self,clazz):
        """Returns true if the object is an instance of clazz."""
        return isinstance(self, clazz)

    def isTypeOf(self, other):
        """Returns true if the object is of the same type as other."""
        return type(self) == type(other)


if __name__ == '__main__':
    a = Element()
    b = Element()
    def cb_func(name, *args):
        print '  cb_func:', name, args

    a.connect('ev1', cb_func, a)
    a.connect('ev1', cb_func, a)
    a.connect('ev2', cb_func, 'ev2', a)

    print 'notify: ev1'
    a.notify('ev1')
    print 'notify: ev2'
    a.notify('ev2')
 
    a.disconnect(cb_func, a)

    print 'notify: ev1'
    a.notify('ev1')
    print 'notify: ev2'
    a.notify('ev2')
 
