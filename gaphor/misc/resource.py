#!/usr/bin/env python
# vim:sw=4:et
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

    def __init__(self, initial_resources={}):
        self._resources.update(initial_resources)
        self._persistent = []
        self._backend = FileBackend()
        self._backend.load(self)

    def __call__(self, r, default=_no_default):
        return self.resource(r, default)

    def save(self):
        self._backend.save(self, self._persistent)

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
        self._backend.update(r, value)


class FileBackend(object):
    """Resource backend that stores data to a resource file
    ($HOME/.gaphor/resource).
    """
    RESOURCE_FILE='resources'
   
    def __init__(self):
        pass

    def get_filename(self, datadir):
        if not os.path.exists(datadir):
            os.mkdir(datadir)
        return os.path.join(datadir, self.RESOURCE_FILE)

    def load(self, resource):
        filename = self.get_filename(resource('UserDataDir'))
        if os.path.exists(filename) and os.path.isfile(filename):
            f = open(filename)
            d = f.read()
            f.close()
            for k, v in eval(d).iteritems():
                resource.set(k, v, persistent=True)

    def save(self, resource, persistent):
        """Save persist resources from the resources dictionary.
        @resource is the Resource instance
        @persistent is a list of persistent resource names.
        """
        filename = self.get_filename(resource('UserDataDir'))
        f = open(filename, 'w')
        persist = dict([(k, v) for k, v in resource._items() if k in persistent])
        pprint.pprint(persist, f)

    def update(self, r, value):
        pass


try:
    import gconf
except ImportError, e:
    pass
else:
    class GConfBackend(object):
        DOMAIN = '/apps/gaphor/'

        def __init__(self):
            self._gconf_client = gconf.client_get_default ()

        def load(self, resources):
            pass

        def save(self, resources, persistent):
            pass

        def update(self, r, value):
            pass


