#!/usr/bin/env python
"""
"""

import sys
import types
import os
import pprint
from zope import interface
from gaphor.interfaces import IService
from gaphas.decorators import async

if os.name == 'nt':
    home = 'USERPROFILE'
else:
    home = 'HOME'

user_data_dir = os.path.join(os.getenv(home), '.gaphor')


_no_default = object()

class Properties(object):
    """
    The Properties class holds a collection of application wide properties.

    Properties are persisted
    """
    interface.implements(IService)

    def __init__(self, backend=None):
        self._resources = {}
        self._backend = backend or FileBackend()

    def init(self, app):
        self._backend.load(self._resources)
    
    def shutdown(self):
        self._backend.save(self._resources)

    def __call__(self, key, default=_no_default):
        return self.get(key, default)

    def save(self):
        self._backend.save(self._resources)

    def _items(self):
        return self._resources.iteritems()

    def dump(self, stream=sys.stdout):
        """
        TODO: define resources that are persistent (have to be saved
        and loaded.
        """
        import pprint
        pprint.pprint(self._resources.items(), stream)

    def get(self, key, default=_no_default):
        """
        Locate a property.

        Resource should be the class of the resource to look for or a string. In
        case of a string the resource will be looked up in the GConf configuration.
        """
        try:
            return self._resources[key]
        except KeyError:
            pass

        if default is not _no_default:
            self.set(key, default)
            return default
        raise KeyError, 'No resource with name "%s"' % key

    def set(self, key, value):
        """
        Set a property to a specific value.

        No smart things are done with classes and class names (like the
        resource() method does).
        """
        resources = self._resources
        resources[key] = value
        self._backend.update(resources, key, value)


class FileBackend(object):
    """
    Resource backend that stores data to a resource file
    ($HOME/.gaphor/resource).
    """
    RESOURCE_FILE='resources'
   
    def __init__(self, datadir=user_data_dir):
        self.datadir = datadir

    def get_filename(self, create=False):
        datadir = self.datadir
        if create and not os.path.exists(datadir):
            os.mkdir(datadir)
        return os.path.join(datadir, self.RESOURCE_FILE)

    def load(self, resource):
        """
        Load resources from a file. Resources are saved like you do with
        a dict().
        """
        filename = self.get_filename()
        if os.path.exists(filename) and os.path.isfile(filename):
            f = open(filename)
            d = f.read()
            f.close()
            for k, v in eval(d).iteritems():
                resource[k] = v

    def save(self, resource):
        """
        Save persist resources from the resources dictionary.
        @resource is the Resource instance
        @persistent is a list of persistent resource names.
        """
        filename = self.get_filename(create=True)
        f = open(filename, 'w')
        try:
            pprint.pprint(resource, f)
        finally:
            f.close()

    @async(single=True, timeout=500)
    def update(self, resource, key, value):
        self.save(resource)


# vim:sw=4:et:ai
