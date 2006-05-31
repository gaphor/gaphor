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
"""Zope 3 Component Architecture

$Id$
"""
import sys
import zope.interface
from types import ClassType
from zope.interface import moduleProvides, Interface
from zope.interface import providedBy, implementedBy
from zope.component.interfaces import IComponentArchitecture
from zope.component.interfaces import IComponentRegistrationConvenience
from zope.component.interfaces import IDefaultViewName
from zope.component.interfaces import IFactory
from zope.component.interfaces import ISiteManager
from zope.component.interfaces import ComponentLookupError
from zope.component.site import globalSiteManager

_class_types = type, ClassType

##############################################################################
# BBB: Import some backward-compatibility; 12/10/2004
from zope.component.bbb import exceptions
sys.modules['zope.component.exceptions'] = exceptions
from zope.component.bbb import service
sys.modules['zope.component.service'] = service
from zope.component.bbb import adapter
sys.modules['zope.component.adapter'] = adapter
from zope.component.bbb import utility
sys.modules['zope.component.utility'] = utility
from zope.component.bbb import servicenames
sys.modules['zope.component.servicenames'] = servicenames
from zope.component.bbb import contextdependent
sys.modules['zope.component.contextdependent'] = contextdependent

from zope.component.bbb import tests as bbb_tests
bbb_tests.__warn__ = False
from zope.component.bbb.tests import placelesssetup
sys.modules['zope.component.tests.placelesssetup'] = placelesssetup
from zope.component.bbb.tests import request
sys.modules['zope.component.tests.request'] = request
from zope.component.bbb.tests import components
sys.modules['zope.component.tests.components'] = components
bbb_tests.__warn__ = True

service.__warn__ = False
service.serviceManager = service.GlobalServiceManager(
    'serviceManager', __name__, globalSiteManager)
service.__warn__ = True

from zope.component.bbb import getGlobalServices, getGlobalService
from zope.component.bbb import getServices, getService
from zope.component.bbb import getServiceDefinitions
from zope.component.bbb import getView, queryView
from zope.component.bbb import getMultiView, queryMultiView
from zope.component.bbb import getViewProviding, queryViewProviding
from zope.component.bbb import getDefaultViewName, queryDefaultViewName
from zope.component.bbb import getResource, queryResource
##############################################################################


# Try to be hookable. Do so in a try/except to avoid a hard dependency.
try:
    from zope.hookable import hookable
except ImportError:
    def hookable(ob):
        return ob

moduleProvides(IComponentArchitecture, IComponentRegistrationConvenience)
__all__ = tuple(IComponentArchitecture)

# SiteManager API

def getGlobalSiteManager():
    return globalSiteManager

def getSiteManager(context=None):
    if context is None:
        return getGlobalSiteManager()
    else:
        # Use the global site manager to adapt context to `ISiteManager`
        # to avoid the recursion implied by using a local `getAdapter()` call.
        try:
            return ISiteManager(context)
        except TypeError, error:
            raise ComponentLookupError(*error.args)

getSiteManager = hookable(getSiteManager)


# Adapter API

def getAdapterInContext(object, interface, context):
    adapter = queryAdapterInContext(object, interface, context)
    if adapter is None:
        raise ComponentLookupError(object, interface)
    return adapter

def queryAdapterInContext(object, interface, context, default=None):
    conform = getattr(object, '__conform__', None)
    if conform is not None:
        try:
            adapter = conform(interface)
        except TypeError:
            # We got a TypeError. It might be an error raised by
            # the __conform__ implementation, or *we* may have
            # made the TypeError by calling an unbound method
            # (object is a class).  In the later case, we behave
            # as though there is no __conform__ method. We can
            # detect this case by checking whether there is more
            # than one traceback object in the traceback chain:
            if sys.exc_info()[2].tb_next is not None:
                # There is more than one entry in the chain, so
                # reraise the error:
                raise
            # This clever trick is from Phillip Eby
        else:
            if adapter is not None:
                return adapter

    if interface.providedBy(object):
        return object

    return getSiteManager(context).queryAdapter(object, interface, '', default)

def getAdapter(object, interface=Interface, name=u'', context=None):
    adapter = queryAdapter(object, interface, name, None, context)
    if adapter is None:
        raise ComponentLookupError(object, interface, name)
    return adapter

def queryAdapter(object, interface=Interface, name=u'', default=None,
                 context=None):
    if context is None:
        return adapter_hook(interface, object, name, default)
    return getSiteManager(context).queryAdapter(object, interface, name,
                                                default)

def getMultiAdapter(objects, interface=Interface, name=u'', context=None):
    adapter = queryMultiAdapter(objects, interface, name, context=context)
    if adapter is None:
        raise ComponentLookupError(objects, interface, name)
    return adapter

def queryMultiAdapter(objects, interface=Interface, name=u'', default=None,
                      context=None):
    try:
        sitemanager = getSiteManager(context)
    except ComponentLookupError:
        # Oh blast, no site manager. This should *never* happen!
        return default

    return sitemanager.queryMultiAdapter(objects, interface, name, default)

def getAdapters(objects, provided, context=None):
    try:
        sitemanager = getSiteManager(context)
    except ComponentLookupError:
        # Oh blast, no site manager. This should *never* happen!
        return []
    return sitemanager.getAdapters(objects, provided)

def subscribers(objects, interface, context=None):
    try:
        sitemanager = getSiteManager(context)
    except ComponentLookupError:
        # Oh blast, no site manager. This should *never* happen!
        return []
    return sitemanager.subscribers(objects, interface)

def handle(*objects):
    sitemanager = getSiteManager(None)
    # iterating over subscribers assures they get executed
    for ignored in sitemanager.subscribers(objects, None):
        pass

class _adapts_descr(object):
    def __init__(self, interfaces):
        self.interfaces = interfaces

    def __get__(self, inst, cls):
        if inst is None:
            return self.interfaces
        raise AttributeError, '__component_adapts__'

class adapter:

    def __init__(self, *interfaces):
        self.interfaces = interfaces

    def __call__(self, ob):
        if isinstance(ob, _class_types):
            ob.__component_adapts__ = _adapts_descr(self.interfaces)
        else:
            ob.__component_adapts__ = self.interfaces

        return ob

def adapts(*interfaces):
    frame = sys._getframe(1)
    locals = frame.f_locals

    # Try to make sure we were called from a class def. In 2.2.0 we can't
    # check for __module__ since it doesn't seem to be added to the locals
    # until later on.
    if (locals is frame.f_globals) or (
        ('__module__' not in locals) and sys.version_info[:3] > (2, 2, 0)):
        raise TypeError("adapts can be used only from a class definition.")

    if '__component_adapts__' in locals:
        raise TypeError("adapts can be used only once in a class definition.")

    locals['__component_adapts__'] = _adapts_descr(interfaces)

def adaptedBy(ob):
    return getattr(ob, '__component_adapts__', None)

#############################################################################
# Register the component architectures adapter hook, with the adapter hook
# registry of the `zope.inteface` package. This way we will be able to call
# interfaces to create adapters for objects. For example, `I1(ob)` is
# equvalent to `getAdapterInContext(I1, ob, '')`.
def adapter_hook(interface, object, name='', default=None):
    try:
        sitemanager = getSiteManager()
    except ComponentLookupError:
        # Oh blast, no site manager. This should *never* happen!
        return None
    return sitemanager.queryAdapter(object, interface, name, default)

# Make the component architecture's adapter hook hookable 
adapter_hook = hookable(adapter_hook)

import zope.interface.interface
zope.interface.interface.adapter_hooks.append(adapter_hook)
#############################################################################


# Utility API

def getUtility(interface, name='', context=None):
    utility = queryUtility(interface, name, context=context)
    if utility is not None:
        return utility
    raise ComponentLookupError(interface, name)

def queryUtility(interface, name='', default=None, context=None):
    return getSiteManager(context).queryUtility(interface, name, default)

def getUtilitiesFor(interface, context=None):
    return getSiteManager(context).getUtilitiesFor(interface)


def getAllUtilitiesRegisteredFor(interface, context=None):
    return getSiteManager(context).getAllUtilitiesRegisteredFor(interface)


# Factories

def createObject(__factory_name, *args, **kwargs):
    # BBB: Goes away in 3.3 
    if not isinstance(__factory_name, basestring):
        import warnings
        warnings.warn(
            "Passing a context as a first argument to createObject is "
            "deprecated.  It will be unsupported in Zope X3.3.  Use a "
            "context keyword argument instead.",
            DeprecationWarning, 2)
        context = __factory_name
        __factory_name, args = args[0], args[1:]
    else:
        context = kwargs.pop('context', None)
    
    return getUtility(IFactory, __factory_name, context)(*args, **kwargs)

def getFactoryInterfaces(name, context=None):
    return getUtility(IFactory, name, context).getInterfaces()

def getFactoriesFor(interface, context=None):
    utils = getSiteManager(context)
    for (name, factory) in utils.getUtilitiesFor(IFactory):
        interfaces = factory.getInterfaces()
        try:
            if interfaces.isOrExtends(interface):
                yield name, factory
        except AttributeError:
            for iface in interfaces:
                if iface.isOrExtends(interface):
                    yield name, factory
                    break


# The following APIs provide registration support for Python code:

def provideUtility(component, provides=None, name=u''):
    if provides is None:
        provides = list(providedBy(component))
        if len(provides) == 1:
            provides = provides[0]
        else:
            raise TypeError("Missing 'provides' argument")

    getGlobalSiteManager().provideUtility(provides, component, name)


def provideAdapter(factory, adapts=None, provides=None, name=''):
    if provides is None:
        provides = list(implementedBy(factory))
        if len(provides) == 1:
            provides = provides[0]
        else:
            raise TypeError("Missing 'provides' argument")

    if adapts is None:
        try:
            adapts = factory.__component_adapts__
        except AttributeError:
            raise TypeError("Missing 'adapts' argument")
            
    getGlobalSiteManager().provideAdapter(adapts, provides, name, factory)

def provideSubscriptionAdapter(factory, adapts=None, provides=None):
    if provides is None:
        provides = list(implementedBy(factory))
        if len(provides) == 1:
            provides = provides[0]
        else:
            raise TypeError("Missing 'provides' argument")

    if adapts is None:
        try:
            adapts = factory.__component_adapts__
        except AttributeError:
            raise TypeError("Missing 'adapts' argument")
            
    getGlobalSiteManager().subscribe(adapts, provides, factory)

def provideHandler(factory, adapts=None):

    if adapts is None:
        try:
            adapts = factory.__component_adapts__
        except AttributeError:
            raise TypeError("Missing 'adapts' argument")
            
    getGlobalSiteManager().subscribe(adapts, None, factory)
