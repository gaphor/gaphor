##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Service Manager implementation

$Id$
"""
__warn__ = True
import warnings

from zope.exceptions import DuplicationError
from zope.component.bbb.interfaces import IServiceService
from zope.interface import implements, Interface, directlyProvides


class IGlobalServiceManager(IServiceService):

    def defineService(name, interface):
        """Define a new service of the given name implementing the given
        interface.  If the name already exists, raises
        DuplicationError"""

    def provideService(name, component):
        """Register a service component.

        Provide a service component to do the work of the named
        service.  If a service component has already been assigned to
        this name, raise DuplicationError; if the name has not been
        defined, raises UndefinedService; if the component does not
        implement the registered interface for the service name,
        raises InvalidService.

        """

class IService(Interface):
    """Marker interface that is used as utility interface to simulate
       services."""

class IServiceDefinition(Interface):
    """Marker interface that is used as utility interface to store service
    defintions (name, interface)."""

class UndefinedService(Exception):
    """An attempt to register a service that has not been defined
    """

class InvalidService(Exception):
    """An attempt to register a service that doesn't implement
       the required interface
    """

class GlobalServiceManager(object):
    """service manager"""

    implements(IGlobalServiceManager)

    def __init__(self, name=None, module=None, sitemanager=None):
        if __warn__:
            warnings.warn(
                "The concept of services has been deprecated. You now have "
                "only adapters and utilities, which are managed by the site "
                "manager, which is probably the object you want.",
                DeprecationWarning, 2)
        if sitemanager is None:
            from zope.component.site import GlobalSiteManager
            sitemanager = GlobalSiteManager()
        self.sm = sitemanager
        self.__name__ = name
        self.__module__ = module

    def _clear(self):
        pass

    def __reduce__(self):
        # Global service managers are pickled as global objects
        return self.__name__

    def defineService(self, name, interface):
        """see IGlobalServiceManager interface"""

        utils = self.sm.getAllUtilitiesRegisteredFor(IServiceDefinition)
        names = [n for n, iface in utils]
        if name in names:
            raise DuplicationError(name)

        self.sm.provideUtility(IServiceDefinition, (name, interface),
                                name=name, strict=False)

    def getServiceDefinitions(self):
        """see IServiceService Interface"""
        defs = list(self.sm.getAllUtilitiesRegisteredFor(IServiceDefinition))
        return defs + [('Services', IServiceService)]

    def provideService(self, name, component, force=False):
        """see IGlobalServiceManager interface, above

        The force keyword allows one to replace an existing
        service.  This is mostly useful in testing scenarios.
        """

        if not force and self.sm.queryUtility(IService, name) is not None:
            raise DuplicationError(name)

        utils = self.sm.getAllUtilitiesRegisteredFor(IServiceDefinition)
        if name not in [name for name, iface in utils]:
            raise UndefinedService(name)

        if not dict(self.getServiceDefinitions())[name].providedBy(component):
            raise InvalidService(name, component,
                                 dict(self.getServiceDefinitions())[name])

        if isinstance(component, GlobalService):
            component.__parent__ = self
            component.__name__ = name

        # Ignore the base services, since their functionality is provided by
        # the SM.
        if name in ('Adapters', 'Utilities', 'Services'):
            return

        directlyProvides(component, IService)
        self.sm.provideUtility(IService, component, name)

    def getService(self, name):
        """see IServiceService interface"""
        if name == 'Services':
            return self

        if name == 'Adapters':
            from zope.component.bbb.adapter import GlobalAdapterService
            return GlobalAdapterService(self.sm)

        if name == 'Utilities':
            from zope.component.bbb.utility import GlobalUtilityService
            return GlobalUtilityService(self.sm)

        service = self.sm.queryUtility(IService, name)
        if service is None:
            from zope.component.bbb.exceptions import ComponentLookupError
            raise ComponentLookupError(name)

        return service


def GS(service_manager, service_name):
    return service_manager.getService(service_name)

class GlobalService(object):

    def __reduce__(self):
        return GS, (self.__parent__, self.__name__)


def __getSM(sitemanager=None):
    return GlobalServiceManager('serviceManager', __name__, sitemanager)

def defineService(name, interface, sitemanager=None):
    if sitemanager is None:
        from zope.component.site import globalSiteManager
        sitemanager = globalSiteManager
    __getSM(sitemanager).defineService(name, interface)

