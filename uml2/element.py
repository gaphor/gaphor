#!/usr/bin/env python
# vim:sw=4:et
"""Element:

Method names have changed on some places to emphasize that we deal
with a completely new data model here.

save()/load()/postload()
    Load/save the element.

unlink()
    Remove all references to the element. First of all the signal
    '__unlink__' is send to all attached signals.

attach ('name', callback, *data) or
attach (('name', 'other_property'), callback, *data)
    Connect 'callback' to recieve notifications if one of the properties
    change (the latter being more memory efficient if you want to listen on
    more properties). The listener will recieve the property name as
    first argument, followed by *data.

detach (callback, *data)
    Disconnect callback as listener.

notify (name)
    Notify all listeners the property 'name' has changed.
"""

import types

class Element(object):
    """Base class for UML data classes."""

    def __init__(self):
	self._observers = dict()

    def save(self, save_func):
	"""Save the state by calling save_func(name, value)."""
        lst = dir(self.__class__)
        for prop in map(isinstance, lst, [umlproperty] * len(lst)):
                prop.save(self, save_func)

    def load(self, name, value):
	"""Loads value in name. Make sure that for every load postload()
	should be called."""
	try:
            prop = getattr(self.__class__, name)
        except AttributeError, e:
            raise AttributeError, "'%s' has no property '%s'" % \
                                        (self.__class__.__name__, name)
        else:
            prop.load(self, value)

    def postload(self):
	pass

    def unlink(self):
	self.notify('__unlink__')
           
    def attach(self, names, callback, *data):
	"""Attach 'callback' to a list of names. Names may also be a string."""
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

    def detach(self, callback, *data):
	"""Detach a callback identified by it's data."""
        #print 'detach', callback, data
        cb = (callback,) + data
	for values in self._observers.values():
            # Remove all occurences of 'cb' from values
            # (if none is found ValueError is raised).
            try:
                while True:
                    values.remove(cb)
            except ValueError:
                pass

    def notify(self, name):
        """Send notification to attached callbacks that a property
	has changed."""
	cb_list = self._observers.get(name) or ()
        for cb_data in cb_list:
            try:
                apply(cb_data[0], (name,) + cb_data[1:])
            except:
                pass

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

    a.attach('ev1', cb_func, a)
    a.attach('ev1', cb_func, a)
    a.attach('ev2', cb_func, 'ev2', a)

    print 'notify: ev1'
    a.notify('ev1')
    print 'notify: ev2'
    a.notify('ev2')
 
    a.detach(cb_func, a)

    print 'notify: ev1'
    a.notify('ev1')
    print 'notify: ev2'
    a.notify('ev2')
 
