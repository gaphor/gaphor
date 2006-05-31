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
"""API tests

$Id$
"""
import unittest

from zope import component
from zope.component import servicenames
from zope.component import getAdapter, queryAdapter, getAdapters
from zope.component import getAdapterInContext, queryAdapterInContext
from zope.component import getService
from zope.component import getUtility, queryUtility
from zope.component import getDefaultViewName
from zope.component import queryMultiAdapter
from zope.component.exceptions import ComponentLookupError
from zope.component.servicenames import Adapters
from zope.component.tests.placelesssetup import PlacelessSetup
from zope.component.tests.request import Request
from zope.component.interfaces import IComponentArchitecture, IServiceService
from zope.component.interfaces import IDefaultViewName

from zope.interface import Interface, implements
from zope.interface.verify import verifyObject

class I1(Interface):
    pass
class I2(Interface):
    pass
class I3(Interface):
    pass

class Comp(object):
    implements(I2)
    def __init__(self, context, request=None): self.context = context

class Comp2(object):
    implements(I3)
    def __init__(self, context, request=None): self.context = context

comp = Comp(1)

class Ob(object):
    implements(I1)
    def __conform__(self, i):
        if i is IServiceService:
            from zope.component.bbb import getServices
            return getServices()
        from zope.component.interfaces import ISiteManager
        from zope.component import getSiteManager
        if i is ISiteManager:
            return getSiteManager()


ob = Ob()

class Conforming(Ob):
    def __conform__(self, i):
        if i is I3:
            return Comp(self)
        else:
            return Ob.__conform__(self, i)

class StubServiceService(object):
    implements(IServiceService)  # This is a lie.

    def __init__(self):
        self.services = {}
        from zope.component.site import GlobalSiteManager
        self.sm = GlobalSiteManager()

    def setService(self, name, service):
        self.services[name] = service

    def getService(self, name):
        try:
            return self.services[name]
        except KeyError:
            raise ComponentLookupError, name

class ConformsToIServiceService(object):

    def __init__(self, serviceservice):
        self.serviceservice = serviceservice

    def __conform__(self, interface):
        if interface is IServiceService:
            return self.serviceservice
        from zope.component.interfaces import ISiteManager
        if interface is ISiteManager:
            return self.serviceservice.sm


class Test(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        from zope.component import bbb
        bbb.__warn__ = False
        bbb.service.__warn__ = False

        super(Test, self).setUp()

    def cleanUp(self):
        super(Test, self).cleanUp()
        from zope.component import bbb
        bbb.__warn__ = True
        bbb.service.__warn__ = True

    def testInterfaces(self):
        import zope.component
        self.failUnless(verifyObject(IComponentArchitecture, zope.component))


    def test_getGlobalServices(self):
        from zope.component import getGlobalServices
        from zope.component.service import IGlobalServiceManager

        gsm = getGlobalServices()
        self.assert_(IGlobalServiceManager.providedBy(gsm))
        self.assert_(getGlobalServices().sm is gsm.sm)

    def test_getServices(self):
        from zope.component import getServices

        # We don't know anything about the default service manager, except
        # that it is an IServiceService.
        self.assert_(IServiceService.providedBy(getServices()))

        # Calling getServices with no args is equivalent to calling it
        # with a context of None.
        self.assert_(getServices().sm is getServices(None).sm)

        # If the context passed to getServices is not None, it is
        # adapted to IServiceService and this adapter returned.
        # So, we create a context that can be adapted to IServiceService
        # using the __conform__ API.
        servicemanager = StubServiceService()
        context = ConformsToIServiceService(servicemanager)
        self.assert_(getServices(context) is servicemanager)

        # Using a context that is not adaptable to IServiceService should
        # fail.
        self.assertRaises(ComponentLookupError, getServices, object())

    def test_getService(self):
        from zope.component import getService, getServices

        # Getting the adapter service with no context given is the same
        # as getting the adapter service from the no-context service manager.
        self.assert_(getService(Adapters).sm is
                     getServices().getService(Adapters).sm)
        # And, a context of 'None' is the same as not providing a context.
        self.assert_(getService(Adapters, None).sm is getService(Adapters).sm)

        # If the context is adaptable to IServiceService then we use that
        # adapter.
        servicemanager = StubServiceService()
        adapterservice = object()
        servicemanager.setService(Adapters, adapterservice)
        context = ConformsToIServiceService(servicemanager)
        self.assert_(getService(Adapters, context) is adapterservice)

        # Using a context that is not adaptable to IServiceService should
        # fail.
        self.assertRaises(ComponentLookupError,
                          getService, Adapters, object())

    def testAdapterInContext(self):
        class I1(Interface):
            pass
        class I2(Interface):
            pass
        class C(object):
            implements(I1)
            def __conform__(self, iface, default=None):
                if iface == I2:
                    return 42
                
        ob = C()

        servicemanager = StubServiceService()
        context = ConformsToIServiceService(servicemanager)
        class I3(Interface):
            pass
        servicemanager.sm.provideAdapter((I1,), I3, '', lambda x: 43)

        # If an object implements the interface you want to adapt to,
        # getAdapterInContext should simply return the object.
        self.assertEquals(getAdapterInContext(ob, I1, context), ob)
        self.assertEquals(queryAdapterInContext(ob, I1, context), ob)

        # If an object conforms to the interface you want to adapt to,
        # getAdapterInContext should simply return the conformed object.
        self.assertEquals(getAdapterInContext(ob, I2, context), 42)
        self.assertEquals(queryAdapterInContext(ob, I2, context), 42)

        class I4(Interface):
            pass
        # If an adapter isn't registered for the given object and interface,
        # and you provide no default, raise ComponentLookupError...
        self.assertRaises(ComponentLookupError,
                          getAdapterInContext, ob, I4, context)

        # ...otherwise, you get the default
        self.assertEquals(queryAdapterInContext(ob, I4, context, 44), 44)

        # If you ask for an adapter for which something's registered
        # you get the registered adapter
        self.assertEquals(getAdapterInContext(ob, I3, context), 43)
        self.assertEquals(queryAdapterInContext(ob, I3, context), 43)

    def testAdapter(self):
        # If an adapter isn't registered for the given object and interface,
        # and you provide no default, raise ComponentLookupError...
        self.assertRaises(ComponentLookupError, getAdapter, ob, I2, '')

        # ...otherwise, you get the default
        self.assertEquals(queryAdapter(ob, I2, '', Test), Test)

        getService(Adapters).register([I1], I2, '', Comp)
        c = getAdapter(ob, I2, '')
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

    def testInterfaceCall(self):
        getService(Adapters).register([I1], I2, '', Comp)
        c = I2(ob)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

    def testNamedAdapter(self):
        self.testAdapter()

        # If an adapter isn't registered for the given object and interface,
        # and you provide no default, raise ComponentLookupError...
        self.assertRaises(ComponentLookupError, getAdapter, ob, I2, 'test')

        # ...otherwise, you get the default
        self.assertEquals(queryAdapter(ob, I2, 'test', Test), Test)

        class Comp2(Comp): pass

        getService(Adapters).register([I1], I2, 'test', Comp2)
        c = getAdapter(ob, I2, 'test')
        self.assertEquals(c.__class__, Comp2)
        self.assertEquals(c.context, ob)

    def testQueryMultiAdapter(self):
        # Adapting a combination of 2 objects to an interface
        class DoubleAdapter(object):
            implements(I3)
            def __init__(self, first, second):
                self.first = first
                self.second = second
        class Ob2(object):
            implements(I2)
        ob2 = Ob2()
        context = None
        getService(Adapters, context).register([I1, I2], I3, '', DoubleAdapter)
        c = queryMultiAdapter((ob, ob2), I3, context=context)
        self.assertEquals(c.__class__, DoubleAdapter)
        self.assertEquals(c.first, ob)
        self.assertEquals(c.second, ob2)

    def testAdapterForInterfaceNone(self):

        # providing an adapter for None says that your adapter can
        # adapt anything to I2.
        getService(Adapters).register([None], I2, '', Comp)
        c = I2(ob)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

    def testgetAdapters(self):
        getService(Adapters).register([I1], I2, '', Comp)
        getService(Adapters).register([None], I2, 'foo', Comp)
        c = getAdapters((ob,), I2)
        c.sort()
        self.assertEquals([(name, adapter.__class__, adapter.context)
                           for name, adapter in c],
                          [('', Comp, ob), ('foo', Comp, ob)])

    def testUtility(self):
        self.assertRaises(ComponentLookupError, getUtility, I1, context=ob)
        self.assertRaises(ComponentLookupError, getUtility, I2, context=ob)
        self.assertEquals(queryUtility(I2, default=Test, context=ob), Test)

        getService('Utilities').provideUtility(I2, comp)
        self.assertEquals(id(getUtility(I2, context=ob)), id(comp))

    def testNamedUtility(self):
        from zope.component import getUtility, queryUtility
        from zope.component import getService
        from zope.component.exceptions import ComponentLookupError

        self.testUtility()

        self.assertRaises(ComponentLookupError,
                          getUtility, I1, 'test', context=ob)
        self.assertRaises(ComponentLookupError,
                          getUtility, I2, 'test', context=ob)
        self.assertEquals(queryUtility(I2, 'test', Test, context=ob),
                          Test)

        getService('Utilities').provideUtility(I2, comp, 'test')
        self.assertEquals(id(getUtility(I2, 'test', ob)), id(comp))

    def test_getAllUtilitiesRegisteredFor(self):
        class I21(I2):
            pass
        class Comp21(Comp):
            implements(I21)
        
        compbob = Comp('bob')
        comp21 = Comp21('21')
        comp21bob = Comp21('21bob')
        
        getService('Utilities').provideUtility(I2, comp)
        getService('Utilities').provideUtility(I21, comp21)
        getService('Utilities').provideUtility(I2, compbob, 'bob')
        getService('Utilities').provideUtility(I21, comp21bob, 'bob')

        comps = [comp, compbob, comp21, comp21bob]
        comps.sort()

        uts = list(component.getUtilitiesFor(I2))
        uts.sort()
        self.assertEqual(uts, [('', comp), ('bob', compbob)])

        uts = list(component.getAllUtilitiesRegisteredFor(I2))
        uts.sort()
        self.assertEqual(uts, comps)        

    def testView(self):
        from zope.component import getView, queryView, getService
        from zope.component.exceptions import ComponentLookupError

        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo', Request(I1))
        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo', Request(I2))
        self.assertEquals(queryView(ob, 'foo', Request(I2), Test), Test)

        getService(Adapters).register([I1, I2], Interface, 'foo', Comp)
        c = getView(ob, 'foo', Request(I2))
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo2', Request(I1))
        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo2', Request(I2))
        self.assertEquals(queryView(ob, 'foo2', Request(I2), Test), Test)

        self.assertEquals(queryView(ob, 'foo2', Request(I1), None), None)

    def testView_w_provided(self):
        from zope.component import getView, queryView, getService
        from zope.component.exceptions import ComponentLookupError

        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo', Request(I1), providing=I3)
        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo', Request(I2), providing=I3)
        self.assertEquals(
            queryView(ob, 'foo', Request(I2), Test, providing=I3),
            Test)

        getService(Adapters).register([I1, I2], Interface, 'foo', Comp)

        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo', Request(I1), providing=I3)
        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo', Request(I2), providing=I3)
        self.assertEquals(
            queryView(ob, 'foo', Request(I2), Test, providing=I3),
            Test)

        getService(Adapters).register([I1, I2], I3, 'foo', Comp)

        c = getView(ob, 'foo', Request(I2), providing=I3)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

    def testMultiView(self):
        from zope.component import queryMultiView, getService
        from zope.component.exceptions import ComponentLookupError

        class Ob2(object):
            implements(I2)

        ob2 = Ob2()

        class IRequest(Interface):
            pass

        request = Request(IRequest)

        class MV(object):
            implements(I3)
            def __init__(self, context, other, request):
               self.context, self.other, self.request = context, other, request

        self.assertEquals(
            queryMultiView((ob, ob2), request, I3, 'foo', 42), 42)

        getService(Adapters).register((I1, I2, IRequest), I3, 'foo', MV)

        view = queryMultiView((ob, ob2), request, I3, 'foo')
        self.assertEquals(view.__class__, MV)
        self.assertEquals(view.context, ob)
        self.assertEquals(view.other, ob2)
        self.assertEquals(view.request, request)

    def test_viewProvidingFunctions(self):        
        # Confirm that a call to getViewProving/queryViewProviding simply 
        # passes its arguments through to getView/queryView - here we hack
        # getView and queryView to inspect the args passed through.
        import zope.component

        # hack zope.component.getView
        def getView(object, name, request, context, providing):
            self.args = [object, name, request, context, providing]
        savedGetView = zope.component.getView
        zope.component.bbb.getView = getView

        # confirm pass through of args to getView by way of getViewProviding
        zope.component.getViewProviding(
            object='object', providing='providing', request='request', 
            context='context')
        self.assertEquals(self.args, 
            ['object', '', 'request', 'providing', 'context'])

        # hack zope.component.queryView
        def queryView(object, name, request, default, providing, context):
            self.args = [object, name, request, default, providing, context]
        savedQueryView = zope.component.queryView
        zope.component.bbb.queryView = queryView

        # confirm pass through of args to queryView by way of queryViewProviding
        zope.component.queryViewProviding(
            object='object', providing='providing', request='request', 
            default='default', context='context')
        self.assertEquals(self.args, 
            ['object', '', 'request', 'default', 'providing', 'context'])

        # restore zope.component
        zope.component.bbb.getView = savedGetView
        zope.component.bbb.queryView = savedQueryView

    def testResource(self):
        from zope.component import getResource, queryResource, getService
        from zope.component.exceptions import ComponentLookupError

        r1 = Request(I1)
        r2 = Request(I2)

        self.assertRaises(ComponentLookupError, getResource, 'foo', r1)
        self.assertRaises(ComponentLookupError, getResource, 'foo', r2)
        self.assertEquals(queryResource('foo', r2, Test), Test)

        getService(Adapters).register((I2,), Interface, 'foo', Comp)
        c = getResource('foo', r2)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, r2)

        self.assertRaises(ComponentLookupError, getResource, 'foo2', r1, ob)
        self.assertRaises(ComponentLookupError, getResource, 'foo2', r2)
        self.assertEquals(queryResource('foo2', r2, Test, ob), Test)

        self.assertEquals(queryResource('foo2', r1, None), None)

    def testResource_w_provided(self):
        from zope.component import getResource, queryResource, getService
        from zope.component.exceptions import ComponentLookupError

        r1 = Request(I1)
        r2 = Request(I2)

        self.assertRaises(ComponentLookupError,
                          getResource, 'foo', r1, providing=I3)
        self.assertRaises(ComponentLookupError,
                          getResource, 'foo', r2, providing=I3)
        self.assertEquals(queryResource('foo', r2, Test, providing=I3),
                          Test)

        getService(Adapters).register((I2,), Interface, 'foo', Comp)

        self.assertRaises(ComponentLookupError,
                          getResource, 'foo', r1, providing=I3)
        self.assertRaises(ComponentLookupError,
                          getResource, 'foo', r2, providing=I3)
        self.assertEquals(queryResource('foo', r2, Test, providing=I3),
                          Test)

        getService(Adapters).register((I2,), I3, 'foo', Comp)

        c = getResource('foo', r2, providing=I3)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, r2)

    def testViewWithContextArgument(self):
        # Basically the same as testView, but exercising the context
        # argument. As this only tests global views, the context
        # argument is pretty much a no-operation.
        from zope.component import getView, queryView, getService
        from zope.component.exceptions import ComponentLookupError

        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo', Request(I1), context=ob)
        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo', Request(I2), context=ob)
        self.assertEquals(queryView(ob, 'foo', Request(I2), Test, context=ob),
                          Test)

        getService(Adapters, ob).register((I1, I2), Interface, 'foo', Comp)

        c = getView(ob, 'foo', Request(I2), context=ob)
        self.assertEquals(c.__class__, Comp)
        self.assertEquals(c.context, ob)

        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo2', Request(I1), context=ob)
        self.assertRaises(ComponentLookupError,
                          getView, ob, 'foo2', Request(I2), context=ob)
        self.assertEquals(queryView(ob, 'foo2', Request(I2), Test,
                                    context=ob),
                          Test)

        self.assertEquals(queryView(ob, 'foo2', Request(I1), None,
                                    context=ob),
                          None)

    def testDefaultViewName(self):
        from zope.component import getService
        getService(Adapters).register((I1, I2), IDefaultViewName,
                                      '', 'sample_name')
        self.assertRaises(ComponentLookupError,
                          getDefaultViewName,
                          ob, Request(I1))
        self.assertEquals(getDefaultViewName(ob, Request(I2)),
                          'sample_name')
        self.assertRaises(ComponentLookupError,
                          getDefaultViewName,
                          ob, Request(I1))


class TestNoSetup(unittest.TestCase):

    def testNotBrokenWhenNoService(self):
        # Both of those things emit DeprecationWarnings.
        self.assertRaises(TypeError, I2, ob)
        self.assertEquals(I2(ob, 42), 42)
        pass

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
        unittest.makeSuite(TestNoSetup),
        ))

if __name__ == "__main__":
    unittest.TextTestRunner().run(test_suite())
