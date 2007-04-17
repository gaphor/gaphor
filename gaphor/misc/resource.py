#!/usr/bin/env python
"""
"""

import sys
import types
import os
import pprint

_no_default = object()

class Resource(object):
    """The Resource class holds a collection of application wide resources.
    """
    _resources = {}

    def __init__(self, backend=None, initial_resources={}):
        self._resources.update(initial_resources)
        self._persistent = []
        #self._backend = backend or FileBackend()
        #self._backend.load(self)

    def __call__(self, r, default=_no_default):
        return self.resource(r, default)

    def save(self):
        #self._backend.save(self, self._persistent)
        pass

    def _items(self):
        return self._resources.iteritems()

    def dump(self, stream=sys.stdout):
        """TODO: define resources that are persistent (have to be saved
        and loaded.
        """
        persist = dict([(k, v) for k, v in self._resources.iteritems() if k in self._persistent])
        import pprint
        pprint.pprint(persist, stream)

    def resource(self, r, default=_no_default, persistent=False):
        """Locate a resource.

        Resource should be the class of the resource to look for or a string. In
        case of a string the resource will be looked up in the GConf configuration.

        example: Get the element factory:
                from gaphor import resource, UML
                factory = resource(UML.ElementFactory)

        Also builtin resources are 'Name', 'Version' and 'DataDir'. In case main()
        is run, 'MainWindow' points to the main window of the application.

        If a class name is given as a resource, the resource is created if not
        yet available. If the resource is a string, KeyError is issued if the
        resource could not be localed, unless a default value was set.
        """
        _resources = self._resources

        # Return the existing resource
        try:
            return _resources[r]
        except KeyError:
            pass

        # Handle string-like resources 
        if isinstance (r, types.StringType):
            # TODO: It might be a GConf resource string

            if default is not _no_default:
                self.set(r, default, persistent)
                return default
            raise KeyError, 'No resource with name "%s"' % r

        # Instantiate the resource and return it
        i = r()
        self.set(r, i, persistent)
        self.set(r.__name__, i, persistent)
        return i

    def set(self, r, value, persistent=False):
        """Set a resource to a specific value.
        No smart things are done with classes and class names (like the
        resource() method does).
        """
        self._resources[r] = value
        if persistent or r in self._persistent:
            self.persist(r, value)

    def persist(self, r, value):
        """Save the property to a persistent storage.
        """
        if r not in self._persistent:
            self._persistent.append(r)
        #self._backend.update(r, value)


# vim:sw=4:et
