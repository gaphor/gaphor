##############################################################################
#
# Copyright (c) 2004 Zope Corporation and Contributors.
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
"""Component Architecture API Backward-Compatibility

$Id$
"""
__docformat__ = "reStructuredText"

__warn__ = True

import sys
import warnings

from zope.interface import Interface, providedBy
from zope.component.bbb.interfaces import IServiceService, IDefaultViewName
from zope.component.bbb.service import GlobalServiceManager

# Try to be hookable. Do so in a try/except to avoid a hard dependency.
try:
    from zope.hookable import hookable
except ImportError:
    def hookable(ob):
        return ob

def warningLevel():
    """Returns the number of the first stack frame outside of zope.component"""
    try:
        level = 2
        while sys._getframe(level).f_globals['__name__']=='zope.component.bbb':
            level += 1
        return level
    except ValueError:
        return 2


def getGlobalServices():
    if __warn__:
        warnings.warn(
            "The concept of services has been deprecated. You probably want to "
            "use `getGlobalSiteManager()`.",
            DeprecationWarning, warningLevel())
    from zope.component import getGlobalSiteManager
    return GlobalServiceManager('servicemanager', 'zope.component.service',
                                getGlobalSiteManager())

def getGlobalService(name):
    if __warn__:
        warnings.warn(
            "The concept of services has been deprecated. You probably want to "
            "use `getGlobalSiteManager()` or `getUtility()`.",
            DeprecationWarning, warningLevel())
    return getGlobalServices().getService(name)

def getServices(context=None):
    if __warn__:
        warnings.warn(
            "The concept of services has been deprecated. You probably want to "
            "use `getGlobalSiteManager()` or `getUtility()`.",
            DeprecationWarning, warningLevel())
    if context is None:
        return getGlobalServices()
    else:
        # Use the global service manager to adapt context to IServiceService
        # to avoid the recursion implied by using a local getAdapter call.
        try:
            return IServiceService(context)
        except TypeError, error:
            from zope.component.bbb.exceptions import ComponentLookupError
            raise ComponentLookupError(*error.args)

getServices = hookable(getServices)

def getService(name, context=None):
    if __warn__:
        warnings.warn(
            "The concept of services has been deprecated. You probably want to "
            "use `getGlobalSiteManager()` or `getUtility()`.",
            DeprecationWarning, warningLevel())
    return getServices(context).getService(name)

def getServiceDefinitions(context=None):
    if __warn__:
        warnings.warn(
            "The concept of services has been deprecated.",
            DeprecationWarning, warningLevel())
    return getServices(context).getServiceDefinitions()

# Presentation API

def getView(object, name, request, providing=Interface, context=None):
    if __warn__:
        warnings.warn(
            "The concrete concept of a view has been deprecated. You want to "
            "use `getMultiAdapter((object, request), providing, name, "
            "context)`.",
            DeprecationWarning, warningLevel())
    view = queryView(object, name, request, context=context,
                     providing=providing)
    if view is not None:
        return view

    from zope.component.bbb.exceptions import ComponentLookupError
    raise ComponentLookupError("Couldn't find view",
                               name, object, context, request, providing)

def queryView(object, name, request,
              default=None, providing=Interface, context=None):
    if __warn__:
        warnings.warn(
            "The concrete concept of a view has been deprecated. You want to "
            "use `queryMultiAdapter((object, request), providing, name, "
            "default, context)`.",
            DeprecationWarning, warningLevel())
    from zope.component import queryMultiAdapter
    return queryMultiAdapter((object, request), providing, name,
                             default, context)

queryView = hookable(queryView)

def getMultiView(objects, request, providing=Interface, name='', context=None):
    if __warn__:
        warnings.warn(
            "The concrete concept of a view has been deprecated. You want to "
            "use `getMultiAdapter(objects+(request,), providing, name, "
            "context)`.",
            DeprecationWarning, warningLevel())
    view = queryMultiView(objects, request, providing, name, context=context)
    if view is not None:
        return view

    from zope.component.bbb.exceptions import ComponentLookupError
    raise ComponentLookupError("Couldn't find view",
                               name, objects, context, request)

def queryMultiView(objects, request, providing=Interface, name='',
                   default=None, context=None):
    if __warn__:
        warnings.warn(
            "The concrete concept of a view has been deprecated. You want to "
            "use `getMultiAdapter(objects+(request,), providing, name, "
            "default, context)`.",
            DeprecationWarning, warningLevel())
    from zope.component import queryMultiAdapter
    return queryMultiAdapter(objects+(request,), providing, name,
                             default, context)

def getViewProviding(object, providing, request, context=None):
    if __warn__:
        warnings.warn(
            "The concrete concept of a view has been deprecated. You want to "
            "use `getMultiAdapter((object, request), providing, name, "
            "context)`.",
            DeprecationWarning, warningLevel())
    return getView(object, '', request, providing, context)

def queryViewProviding(object, providing, request, default=None, 
                       context=None):
    if __warn__:
        warnings.warn(
            "The concrete concept of a view has been deprecated. You want to "
            "use `queryMultiAdapter((object, request), providing, name, "
            "default, context)`.",
            DeprecationWarning, warningLevel())
    return queryView(object, '', request, default, providing, context)

def getDefaultViewName(object, request, context=None):
    if __warn__:
        warnings.warn(
            "The concrete concept of a view has been deprecated. You want to "
            "use `getSiteManager(context).adapters.lookup(map(providedBy, "
            "(object, request)), IDefaultViewName)",
            DeprecationWarning, warningLevel())
    view = queryDefaultViewName(object, request, context=context)
    if view is not None:
        return view

    from zope.component.bbb.exceptions import ComponentLookupError
    raise ComponentLookupError("Couldn't find default view name",
                               context, request)

def queryDefaultViewName(object, request, default=None, context=None):
    if __warn__:
        warnings.warn(
            "The concrete concept of a view has been deprecated. You want to "
            "use `getSiteManager(context).adapters.lookup(map(providedBy, "
            "(object, request)), IDefaultViewName)`",
            DeprecationWarning, warningLevel())
    from zope.component.bbb.exceptions import ComponentLookupError
    from zope.component import getSiteManager
    try:
        adapters = getSiteManager(context)
    except ComponentLookupError:
        # Oh blast, no adapter service. We're probably just running from a test
        return default

    name = adapters.adapters.lookup(map(providedBy, (object, request)),
                                    IDefaultViewName)
    if name is not None:
        return name
    return default

def getResource(name, request, providing=Interface, context=None):
    if __warn__:
        warnings.warn(
            "The concrete concept of a resource has been deprecated. You want "
            "to use `getAdapter(request, providing, name, context)`",
            DeprecationWarning, warningLevel())
    view = queryResource(name, request, providing=providing, context=context)
    if view is not None:
        return view

    from zope.component.bbb.exceptions import ComponentLookupError
    raise ComponentLookupError("Couldn't find resource", name, request)

def queryResource(name, request, default=None, providing=Interface,
                  context=None):
    if __warn__:
        warnings.warn(
            "The concrete concept of a resource has been deprecated. You want "
            "to use `queryAdapter(request, providing, name, default, context)`",
            DeprecationWarning, warningLevel())
    from zope.component import queryAdapter
    return queryAdapter(request, providing, name, default, context)


