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
"""Global Adapter Service

$Id$
"""
import sys
import warnings
from types import ClassType

from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IAdapterService, IRegistry
from zope.component.bbb.service import GlobalService
from zope.component.site import AdapterRegistration, SubscriptionRegistration
from zope.interface import implements, providedBy, Interface, implementedBy
from zope.interface.interfaces import IInterface

class IGlobalAdapterService(IAdapterService, IRegistry):

    def register(required, provided, name, factory, info=''):
        """Register an adapter factory

        :Parameters:
          - `required`: a sequence of specifications for objects to be
             adapted. 
          - `provided`: The interface provided by the adapter
          - `name`: The adapter name
          - `factory`: The object used to compute the adapter
          - `info`: Provide some info about this particular adapter.
        """

    def subscribe(required, provided, factory, info=''):
        """Register a subscriber factory

        :Parameters:
          - `required`: a sequence of specifications for objects to be
             adapted. 
          - `provided`: The interface provided by the adapter
          - `name`: The adapter name
          - `factory`: The object used to compute the subscriber
          - `info`: Provide some info about this particular adapter.
        """

class AdapterService(object):
    """Base implementation of an adapter service, implementing only the
    'IAdapterService' interface.

    No write-methods were implemented.
    """

    implements(IAdapterService)

    def __init__(self, sitemanager=None):
        if sitemanager is None:
            from zope.component.site import GlobalSiteManager
            sitemanager = GlobalSiteManager()
        self.sm = sitemanager

    def __getattr__(self, name):
        attr = getattr(self.sm.adapters, name)
        if attr is not None:
            return attr
        raise AttributeError, name


class GlobalAdapterService(AdapterService, GlobalService):
    """Global Adapter Service implementation."""

    implements(IGlobalAdapterService)

    def __init__(self, sitemanager=None):
        super(GlobalAdapterService, self).__init__(sitemanager)

    def register(self, required, provided, name, factory, info=''):
        """Register an adapter

        >>> registry = GlobalAdapterService()
        >>> class R1(Interface):
        ...     pass
        >>> class R2(R1):
        ...     pass
        >>> class P1(Interface):
        ...     pass
        >>> class P2(P1):
        ...     pass

        >>> registry.register((R1, ), P2, 'bob', 'c1', 'd1')
        >>> registry.register((R1, ), P2,    '', 'c2', 'd2')
        >>> registry.lookup((R2, ), P1, '')
        'c2'

        >>> registrations = map(repr, registry.registrations())
        >>> registrations.sort()
        >>> for registration in registrations:
        ...    print registration
        AdapterRegistration(('R1',), 'P2', '', 'c2', 'd2')
        AdapterRegistration(('R1',), 'P2', 'bob', 'c1', 'd1')

        Let's make sure that we can also register regular classes for
        adaptation.

        >>> class O1(object):
        ...     pass
        >>> class O2(object):
        ...     pass
        >>> class O3(object):
        ...     def __init__(self, obj1, obj2=None):
        ...         pass

        >>> registry.register((O1, ), R1, '', O3)
        >>> registry.queryAdapter(O1(), R1, '').__class__
        <class 'zope.component.bbb.adapter.O3'>

        >>> registry.register((O1, O2), R1, '', O3)
        >>> registry.queryMultiAdapter((O1(), O2()), R1, '').__class__
        <class 'zope.component.bbb.adapter.O3'>
        """
        self.sm.provideAdapter(required, provided, name, factory, info)

    def subscribe(self, required, provided, factory, info=''):
        """Register an subscriptions adapter

        >>> registry = GlobalAdapterService()
        >>> class R1(Interface):
        ...     pass
        >>> class R2(R1):
        ...     pass
        >>> class P1(Interface):
        ...     pass
        >>> class P2(P1):
        ...     pass

        >>> registry.subscribe((R1, ), P2, 'c1', 'd1')
        >>> registry.subscribe((R1, ), P2, 'c2', 'd2')
        >>> subscriptions = map(str, registry.subscriptions((R2, ), P1))
        >>> subscriptions.sort()
        >>> subscriptions
        ['c1', 'c2']

        >>> registrations = map(repr, registry.registrations())
        >>> registrations.sort()
        >>> for registration in registrations:
        ...    print registration
        SubscriptionRegistration(('R1',), 'P2', 'c1', 'd1')
        SubscriptionRegistration(('R1',), 'P2', 'c2', 'd2')

        """
        self.sm.subscribe(required, provided, factory, info)

    def registrations(self):
        for registration in self.sm.registrations():
            if isinstance(registration,
                          (AdapterRegistration, SubscriptionRegistration)):
                yield registration
