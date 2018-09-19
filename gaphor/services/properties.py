#!/usr/bin/env python

# Copyright (C) 2007-2017 Adam Boduch <adam.boduch@gmail.com>
#                         Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License 
# more details.
#
# You should have received a copy of the GNU Library General Public 
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""The properties module allows Gaphor properties to be saved to the local
file system.  These are things like preferences."""

from __future__ import absolute_import
import sys
import os
import pprint
from zope import interface

from gaphor.core import inject
from logging import getLogger
from gaphor.interfaces import IService
from gaphas.decorators import async
from gaphor.misc import get_user_data_dir
import six

class IPropertyChangeEvent(interface.Interface):
    
    """A property changed event has a name, an old value, and a new value."""

    name = interface.Attribute("The property name")
    old_value = interface.Attribute("The property value before the change")
    new_value = interface.Attribute("The property value after the change")


class PropertyChangeEvent(object):
    
    """This event is triggered any time a property is changed.  This event
    holds the property name, the current value, and the new value."""
    
    interface.implements(IPropertyChangeEvent)

    def __init__(self, name, old_value, new_value):
        self.name = name
        self.old_value = old_value
        self.new_value = new_value

_no_default = object()

class Properties(object):
    """The Properties class holds a collection of application wide properties.

    Properties are persisted to the local file system."""
    
    interface.implements(IService)

    component_registry = inject('component_registry')

    logger = getLogger('Properties')

    def __init__(self, backend=None):
        """Constructor.  Initialize the Gaphor application object, the
        dictionary for storing properties in memory, and the storage backend.
        This defaults to FileBackend"""
        
        self._resources = {}
        self._backend = backend or FileBackend()

    def init(self, app):
        """Initialize the properties service.  This will load any stored 
        properties from the file system."""
        
        self._backend.load(self._resources)
    
    def shutdown(self):
        """Shutdown the properties service.  This will ensure that all 
        properties are saved."""
        
        self._backend.save(self._resources)

    def __call__(self, key, default=_no_default):
        """Retrieve the specified property.  If the property doesn't exist,
        the default parameter is returned.  This defaults to _no_default."""
        
        return self.get(key, default)

    def save(self):
        """Save all properties by calling save() on the properties storage
        backend."""
        
        self._backend.save(self._resources)

    def _items(self):
        """Return an iterator for all stored properties."""
        
        return six.iteritems(self._resources)

    def dump(self, stream=sys.stdout):
        """
        TODO: define resources that are persistent (have to be saved
        and loaded.
        """
        pprint.pprint(list(self._resources.items()), stream)

    def get(self, key, default=_no_default):
        """Locate a property.

        Resource should be the class of the resource to look for or a string. In
        case of a string the resource will be looked up in the GConf
        configuration."""
        
        try:
            return self._resources[key]
        except KeyError:
            if default is _no_default:
                raise KeyError('No resource with name "%s"' % key)

            self.set(key, default)
            return default

    def set(self, key, value):
        """Set a property to a specific value.

        No smart things are done with classes and class names (like the
        resource() method does)."""
        
        resources = self._resources
        old_value = resources.get(key)
        
        if value != old_value:
            resources[key] = value
            self.component_registry.handle(PropertyChangeEvent(key, old_value, value))
            self._backend.update(resources, key, value)

class FileBackend(object):
    """Resource backend that stores data to a resource file
    ($HOME/.gaphor/resource)."""
    
    RESOURCE_FILE='resources'
   
    def __init__(self, datadir=get_user_data_dir()):
        """Constructor.  Initialize the directory used for storing 
        properties."""
        
        self.datadir = datadir

    def get_filename(self, create=False):
        """Return the current file used to store Gaphor properties.  If the
        created parameter is set to True, the file is created if it doesn't 
        exist.  This defaults to False."""
        
        datadir = self.datadir
        
        if create and not os.path.exists(datadir):
            os.mkdir(datadir)
        
        return os.path.join(datadir, self.RESOURCE_FILE)

    def load(self, resource):
        """Load resources from a file. Resources are saved like you do with
        a dict()."""
        
        filename = self.get_filename()
        
        if os.path.exists(filename) and os.path.isfile(filename):

            with open(filename) as ifile:
                data = ifile.read()
                
            for key, value in six.iteritems(eval(data)):
                resource[key] = value

    def save(self, resource):
        """Save persist resources from the resources dictionary.
        @resource is the Resource instance
        @persistent is a list of persistent resource names.
        """
        
        filename = self.get_filename(create=True)
        
        with open(filename, 'w') as ofile:
            pprint.pprint(resource, ofile)

    @async(single=True, timeout=500)
    def update(self, resource, key, value):
        """Update the properties file with any changes in the background."""
        
        self.save(resource)
