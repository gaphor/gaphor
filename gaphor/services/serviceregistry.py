#!/usr/bin/env python

# Copyright (C) 2009-2017 Adam Boduch <adam.boduch@gmail.com>
#                         Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 2 of the License, or (at your option) any later
# version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
The service registry is the place where services can be registered and
retrieved.

Our good old NameServicer.
"""

from __future__ import absolute_import
from zope import interface, component

from logging import getLogger
from gaphor.interfaces import IService
from gaphor.core import inject
import six

class ServiceRegistry(object):

    component_registry = inject('component_registry')
    logger = getLogger('ServiceRegistry')

    def __init__(self):
        self._uninitialized_services = {}


    def init(self, app=None):
        self.logger.info('Starting')
        

    def shutdown(self):
        
        self.logger.info('Shutting down')


    def load_services(self, services=None):
        """
        Load services from resources.

        Services are registered as utilities in zope.component.
        Service should provide an interface gaphor.interfaces.IService.
        """
        
        self.logger.info('Loading services')
        
        for ep in pkg_resources.iter_entry_points('gaphor.services'):
            cls = ep.load()
            if not IService.implementedBy(cls):
                raise MisConfigurationException('Entry point %s doesn''t provide IService' % ep.name)
            if services is None or ep.name in services:
                srv = cls()
                self._uninitialized_services[ep.name] = srv

    def init_all_services(self):
        
        self.logger.info('Initializing services')
        
        while self._uninitialized_services:
            self.init_service(six.iterkeys(self._uninitialized_services))

    def init_service(self, name):
        """
        Initialize a not yet initialized service.

        Raises ComponentLookupError if the service has nor been found
        """
        
        self.logger.info('Initializing service')
        self.logger.debug('Service name is %s' % name)
        
        try:
            srv = self._uninitialized_services.pop(name)
        except KeyError:
            raise component.ComponentLookupError(IService, name)
        else:
            srv.init(self)
            self.component_registry.register_utility(srv, IService, name)
            self.handle(ServiceInitializedEvent(name, srv))
            return srv

    def get_service(self, name):
        try:
            return self.component_registry.get_utility(IService, name)
        except component.ComponentLookupError:
            return self.init_service(name)


# vim: sw=4:et:ai
