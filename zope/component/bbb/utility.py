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
"""utility service

$Id$
"""
from zope.component.exceptions import Invalid, ComponentLookupError
from zope.component.interfaces import IUtilityService, IRegistry
from zope.component.service import GlobalService, IService, IServiceDefinition
from zope.component.site import UtilityRegistration
import zope.interface

class IGlobalUtilityService(IUtilityService, IRegistry):

    def provideUtility(providedInterface, component, name='', info=''):
        """Provide a utility

        A utility is a component that provides an interface.
        """

class UtilityService(object):
    """Provide IUtilityService

    Mixin that superimposes utility management on adapter registery
    implementation
    """

    def __init__(self, sitemanager=None):
        self.__parent__ = None
        if sitemanager is None:
            from zope.component.site import GlobalSiteManager
            sitemanager = GlobalSiteManager()
        self.sm = sitemanager

    def __getattr__(self, name):
        attr = getattr(self.sm, name)
        if attr is not None:
            return attr

        attr = getattr(self.sm.utilities, name)
        if attr is not None:
            return attr

        raise AttributeError, name


class GlobalUtilityService(UtilityService, GlobalService):

    zope.interface.implementsOnly(IGlobalUtilityService)

    def __init__(self, sitemanager=None):
        super(GlobalUtilityService, self).__init__(sitemanager)

    def provideUtility(self, providedInterface, component, name='', info=''):
        self.sm.provideUtility(providedInterface, component, name, info)

    def registrations(self):
        for reg in self.sm.registrations():
            if isinstance(reg, UtilityRegistration):
                if not reg.provided in (IService, IServiceDefinition): 
                    yield reg
