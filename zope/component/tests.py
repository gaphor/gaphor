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
"""Component Architecture Tests

$Id$
"""
import unittest

from zope.interface import Interface, implements
from zope.interface.verify import verifyObject
from zope.testing import doctest

import zope.component
from zope.component.interfaces import ComponentLookupError
from zope.component.interfaces import IComponentArchitecture
from zope.component.interfaces import ISiteManager
from zope.component.testing import setUp, tearDown

class I1(Interface):
    pass
class I2(Interface):
    pass
class I3(Interface):
    pass

class Ob(object):
    implements(I1)
    def __repr__(self):
        return '<instance Ob>'


ob = Ob()

class Ob2(object):
    implements(I2)
    def __repr__(self):
        return '<instance Ob2>'

class Comp(object):
    implements(I2)
    def __init__(self, context):
        self.context = context

comp = Comp(1)

class Comp2(object):
    implements(I3)
    def __init__(self, context):
        self.context = context


class ConformsToISiteManager(object):
    """This object allows the sitemanager to conform/adapt to `ISiteManager`
    and thus to itself."""

    def __init__(self, sitemanager):
        self.sitemanager = sitemanager

    def __conform__(self, interface):
        """This method is specified by the adapter PEP to do the adaptation."""
        if interface is ISiteManager:
            return self.sitemanager


def testInterfaces():
    """Ensure that the component architecture API is provided by
    `zope.component`.
    
    >>> import zope.component
    >>> verifyObject(IComponentArchitecture, zope.component)
    True
    """

def test_getGlobalSiteManager():
    """One of the most important functions is to get the global site manager.
    
      >>> from zope.component.site import IGlobalSiteManager, globalSiteManager

    Get the global site manager via the CA API function:

      >>> gsm = zope.component.getGlobalSiteManager()

    Make sure that the global site manager implements the correct interface
    and is the global site manager instance we expect to get.
    
      >>> IGlobalSiteManager.providedBy(gsm)
      True
      >>> globalSiteManager is gsm
      True

    Finally, ensure that we always get the same global site manager, otherwise
    our component registry will always be reset. 

      >>> zope.component.getGlobalSiteManager() is gsm
      True
    """

def test_getSiteManager():
    """Make sure that `getSiteManager()` always returns the correct site
    manager instance.
    
    We don't know anything about the default service manager, except that it
    is an `ISiteManager`.

      >>> ISiteManager.providedBy(zope.component.getSiteManager())
      True

    Calling `getSiteManager()` with no args is equivalent to calling it with a
    context of `None`.

      >>> zope.component.getSiteManager() is zope.component.getSiteManager(None)
      True
      
    If the context passed to `getSiteManager()` is not `None`, it is adapted
    to `ISiteManager` and this adapter returned.  So, we create a context that
    can be adapted to `ISiteManager` using the `__conform__` API.

    Let's create the simplest stub-implementation of a site manager possible:

      >>> sitemanager = object()

    Now create a context that knows how to adapt to our newly created site
    manager.
    
      >>> context = ConformsToISiteManager(sitemanager)

    Now make sure that the `getSiteManager()` API call returns the correct
    site manager.

      >>> zope.component.getSiteManager(context) is sitemanager
      True

    Using a context that is not adaptable to `ISiteManager` should fail.

      >>> zope.component.getSiteManager(ob) #doctest: +NORMALIZE_WHITESPACE
      Traceback (most recent call last):
      ...
      ComponentLookupError: ('Could not adapt', <instance Ob>,
      <InterfaceClass zope.component.interfaces.ISiteManager>)
    """
    
def testAdapterInContext(self):
    """The `getAdapterInContext()` and `queryAdapterInContext()` API functions
    do not only use the site manager to look up the adapter, but first tries
    to use the `__conform__()` method of the object to find an adapter as
    specified by PEP 246.

    Let's start by creating a component that support's the PEP 246's
    `__conform__()` method:
    
      >>> class Component(object):
      ...     implements(I1)
      ...     def __conform__(self, iface, default=None):
      ...         if iface == I2:
      ...             return 42
      ...     def __repr__(self):
      ...         return '''<Component implementing 'I1'>'''
      
      >>> ob = Component()
      
    We also gave the component a custom representation, so it will be easier
    to use in these tests.

    We now have to create a site manager (other than the default global one)
    with which we can register adapters for `I1`.
      
      >>> from zope.component.site import GlobalSiteManager
      >>> sitemanager = GlobalSiteManager()

    Now we create a new `context` that knows how to get to our custom site
    manager.
    
      >>> context = ConformsToISiteManager(sitemanager)

    We now register an adapter from `I1` to `I3`:
      
      >>> sitemanager.provideAdapter((I1,), I3, '', lambda x: 43)

    If an object implements the interface you want to adapt to,
    `getAdapterInContext()` should simply return the object.

      >>> zope.component.getAdapterInContext(ob, I1, context)
      <Component implementing 'I1'>
      >>> zope.component.queryAdapterInContext(ob, I1, context)
      <Component implementing 'I1'>

    If an object conforms to the interface you want to adapt to,
    `getAdapterInContext()` should simply return the conformed object.

      >>> zope.component.getAdapterInContext(ob, I2, context)
      42
      >>> zope.component.queryAdapterInContext(ob, I2, context)
      42

    If an adapter isn't registered for the given object and interface, and you
    provide no default, raise ComponentLookupError...

      >>> class I4(Interface):
      ...     pass

      >>> zope.component.getAdapterInContext(ob, I4, context) \\
      ... #doctest: +NORMALIZE_WHITESPACE
      Traceback (most recent call last):
      ...
      ComponentLookupError: (<Component implementing 'I1'>,
                             <InterfaceClass zope.component.tests.I4>)

    ...otherwise, you get the default:

      >>> zope.component.queryAdapterInContext(ob, I4, context, 44)
      44

    If you ask for an adapter for which something's registered you get the
    registered adapter

      >>> zope.component.getAdapterInContext(ob, I3, context)
      43
      >>> zope.component.queryAdapterInContext(ob, I3, context)
      43
    """

def testAdapter():
    """The `getAdapter()` and `queryAdapter()` API functions are similar to
    `{get|query}AdapterInContext()` functions, except that they do not care
    about the `__conform__()` but also handle named adapters. (Actually, the
    name is a required argument.)
    
    If an adapter isn't registered for the given object and interface, and you
    provide no default, raise `ComponentLookupError`...

      >>> zope.component.getAdapter(ob, I2, '') #doctest: +NORMALIZE_WHITESPACE
      Traceback (most recent call last):
      ...
      ComponentLookupError: (<instance Ob>,
                             <InterfaceClass zope.component.tests.I2>,
                             '')

    ...otherwise, you get the default

      >>> zope.component.queryAdapter(ob, I2, '', '<default>')
      '<default>'

    Now get the global site manager and register an adapter from `I1` to `I2`
    without a name:
      
      >>> zope.component.getGlobalSiteManager().provideAdapter(
      ...     (I1,), I2, '', Comp)

    You can now simply access the adapter using the `getAdapter()` API
    function:

      >>> adapter = zope.component.getAdapter(ob, I2, '')
      >>> adapter.__class__ is Comp
      True
      >>> adapter.context is ob
      True
    """

def testInterfaceCall():
    """Here we test the `adapter_hook()` function that we registered with the
    `zope.interface` adapter hook registry, so that we can call interfaces to
    do adaptation.

    First, we need to register an adapter:
    
      >>> zope.component.getGlobalSiteManager().provideAdapter(
      ...     [I1], I2, '', Comp)

    Then we try to adapt `ob` to provide an `I2` interface by calling the `I2`
    interface with the obejct as first argument:

      >>> adapter = I2(ob)
      >>> adapter.__class__ is Comp
      True
      >>> adapter.context is ob
      True

    If no adapter is found, a `TypeError is raised...

      >>> I1(Ob2()) #doctest: +NORMALIZE_WHITESPACE
      Traceback (most recent call last):
      ...
      TypeError: ('Could not adapt', <instance Ob2>,
                  <InterfaceClass zope.component.tests.I1>)
      
    ...unless we specify an alternative adapter:

      >>> marker = object()
      >>> I2(object(), marker) is marker
      True
    """

def testNamedAdapter():
    """Make sure that adapters with names are correctly selected from the
    registry.

    First we register some named adapter:

      >>> zope.component.getGlobalSiteManager().provideAdapter(
      ...     [I1], I2, 'foo', lambda x: 0)

    If an adapter isn't registered for the given object and interface,
    and you provide no default, raise `ComponentLookupError`...

      >>> zope.component.getAdapter(ob, I2, 'bar') \\
      ... #doctest: +NORMALIZE_WHITESPACE
      Traceback (most recent call last):
      ...
      ComponentLookupError: 
      (<instance Ob>, <InterfaceClass zope.component.tests.I2>, 'bar')

    ...otherwise, you get the default

      >>> zope.component.queryAdapter(ob, I2, 'bar', '<default>')
      '<default>'

    But now we register an adapter for the object having the correct name

      >>> zope.component.getGlobalSiteManager().provideAdapter(
      ...     [I1], I2, 'bar', Comp)

    so that the lookup succeeds:
    
      >>> adapter = zope.component.getAdapter(ob, I2, 'bar')
      >>> adapter.__class__ is Comp
      True
      >>> adapter.context is ob
      True
    """

def testMultiAdapter():
    """Adapting a combination of 2 objects to an interface

    Multi-adapters adapt one or more objects to another interface. To make
    this demonstration non-trivial, we need to create a second object to be
    adapted:
    
      >>> ob2 = Ob2()

    Like for regular adapters, if an adapter isn't registered for the given
    objects and interface, and you provide no default, raise
    `ComponentLookupError`...

      >>> zope.component.getMultiAdapter((ob, ob2), I3) \\
      ... #doctest: +NORMALIZE_WHITESPACE
      Traceback (most recent call last):
      ...
      ComponentLookupError:
      ((<instance Ob>, <instance Ob2>),
       <InterfaceClass zope.component.tests.I3>,
       u'')

    ...otherwise, you get the default

      >>> zope.component.queryMultiAdapter((ob, ob2), I3, default='<default>')
      '<default>'

    Note that the name is not a required attribute here.

    To test multi-adapters, we also have to create an adapter class that
    handles to context objects:
    
      >>> class DoubleAdapter(object):
      ...     implements(I3)
      ...     def __init__(self, first, second):
      ...         self.first = first
      ...         self.second = second

    Now we can register the multi-adapter using
    
      >>> zope.component.getGlobalSiteManager().provideAdapter(
      ...     (I1, I2), I3, '', DoubleAdapter)

    Notice how the required interfaces are simply provided by a tuple. Now we
    can get the adapter:

      >>> adapter = zope.component.getMultiAdapter((ob, ob2), I3)
      >>> adapter.__class__ is DoubleAdapter
      True
      >>> adapter.first is ob
      True
      >>> adapter.second is ob2
      True
    """

def testAdapterForInterfaceNone():
    """Providing an adapter for None says that your adapter can adapt anything
    to `I2`.

      >>> zope.component.getGlobalSiteManager().provideAdapter(
      ...     (None,), I2, '', Comp)

      >>> adapter = I2(ob)
      >>> adapter.__class__ is Comp
      True
      >>> adapter.context is ob
      True

    It can really adapt any arbitrary object:

      >>> something = object()
      >>> adapter = I2(something)
      >>> adapter.__class__ is Comp
      True
      >>> adapter.context is something
      True
    """
    
def testGetAdapters():
    """It is sometimes desireable to get a list of all adapters that are
    registered for a particular output interface, given a set of
    objects.

    Let's register some adapters first: 
    
      >>> zope.component.getGlobalSiteManager().provideAdapter(
      ...     [I1], I2, '', Comp)
      >>> zope.component.getGlobalSiteManager().provideAdapter(
      ...     [None], I2, 'foo', Comp)

    Now we get all the adapters that are registered for `ob` that provide
    `I2`:
    
      >>> adapters = zope.component.getAdapters((ob,), I2)
      >>> adapters.sort()
      >>> [(name, adapter.__class__.__name__) for name, adapter in adapters]
      [(u'', 'Comp'), (u'foo', 'Comp')]

    Note that the output doesn't include None values. If an adapter
    factory returns None, it is as if it wasn't present.

      >>> zope.component.getGlobalSiteManager().provideAdapter(
      ...     [I1], I2, 'nah', lambda context: None)
      >>> adapters = zope.component.getAdapters((ob,), I2)
      >>> adapters.sort()
      >>> [(name, adapter.__class__.__name__) for name, adapter in adapters]
      [(u'', 'Comp'), (u'foo', 'Comp')]
      

    """

def testUtility():
    """Utilities are components that simply provide an interface. They are
    instantiated at the time or before they are registered. Here we test the
    simple query interface.

    Before we register any utility, there is no utility available, of
    course. The pure instatiation of an object does not make it a utility. If
    you do not specify a default, you get a `ComponentLookupError`...

      >>> zope.component.getUtility(I1) #doctest: +NORMALIZE_WHITESPACE
      Traceback (most recent call last):
      ...
      ComponentLookupError: \
      (<InterfaceClass zope.component.tests.I1>, '')

    ...otherwise, you get the default

      >>> zope.component.queryUtility(I1, default='<default>')
      '<default>'
      >>> zope.component.queryUtility(I2, default='<default>')
      '<default>'

    Now we declare `ob` to be the utility providing `I1`

      >>> zope.component.getGlobalSiteManager().provideUtility(I1, ob)

    so that the component is now available:
    
      >>> zope.component.getUtility(I1) is ob
      True
    """

def testNamedUtility():
    """Like adapters, utilities can be named.

    Just because you register an utility having no name
    
      >>> zope.component.getGlobalSiteManager().provideUtility(I1, ob)

    does not mean that they are available when you specify a name:
    
      >>> zope.component.getUtility(I1, name='foo') \\
      ... #doctest: +NORMALIZE_WHITESPACE
      Traceback (most recent call last):
      ...
      ComponentLookupError:
      (<InterfaceClass zope.component.tests.I1>, 'foo')


    ...otherwise, you get the default

      >>> zope.component.queryUtility(I1, name='foo', default='<default>')
      '<default>'

    Registering the utility under the correct name 

      >>> zope.component.getGlobalSiteManager().provideUtility(
      ...     I1, ob, name='foo')

    really helps:

      >>> zope.component.getUtility(I1, 'foo') is ob
      True
    """

def test_getAllUtilitiesRegisteredFor():
    """Again, like for adapters, it is often useful to get a list of all
    utilities that have been registered for a particular interface. Utilities
    providing a derived interface are also listed.

    Thus, let's create a derivative interface of `I1`:
    
      >>> class I11(I1):
      ...     pass

      >>> class Ob11(Ob):
      ...     implements(I11)
    
      >>> ob11 = Ob11()
      >>> ob_bob = Ob()

    Now we register the new utilities:

      >>> gsm = zope.component.getGlobalSiteManager()
      >>> gsm.provideUtility(I1, ob)
      >>> gsm.provideUtility(I11, ob11)
      >>> gsm.provideUtility(I1, ob_bob, name='bob')
      >>> gsm.provideUtility(I2, Comp(2))

    We can now get all the utilities that provide interface `I1`:

      >>> uts = list(zope.component.getAllUtilitiesRegisteredFor(I1))
      >>> uts = [util.__class__.__name__ for util in uts]
      >>> uts.sort()
      >>> uts
      ['Ob', 'Ob', 'Ob11']

    Note that `getAllUtilitiesRegisteredFor()` does not return the names of
    the utilities.
    """

def testNotBrokenWhenNoSiteManager():
    """Make sure that the adapter lookup is not broken, when no site manager
    is available.

    Both of those things emit `DeprecationWarnings`.

      >>> I2(ob) #doctest: +NORMALIZE_WHITESPACE
      Traceback (most recent call last):
      ...
      TypeError: ('Could not adapt',
                  <instance Ob>,
                  <InterfaceClass zope.component.tests.I2>)


      >>> I2(ob, 42)
      42
    """


def testNo__component_adapts__leakage():
    """
    We want to make sure that an `adapts()` call in a class definition
    doesn't affect instances.

      >>> import zope.component
      >>> class C:
      ...     zope.component.adapts()

      >>> C.__component_adapts__
      ()
      >>> C().__component_adapts__
      Traceback (most recent call last):
      ...
      AttributeError: __component_adapts__
    """

def test_ability_to_pickle_globalsitemanager():
    """
    We need to make sure that it is possible to pickle the global site manager
    and its two global adapter registries.

      >>> from zope.component import site
      >>> import cPickle
      >>> pickle = cPickle.dumps(site.globalSiteManager)
      >>> sm = cPickle.loads(pickle)
      >>> sm is site.globalSiteManager
      True

    Now let's ensure that the registries themselves can be pickled as well:

      >>> pickle = cPickle.dumps(site.globalSiteManager.adapters)
      >>> adapters = cPickle.loads(pickle)
      >>> adapters is site.globalSiteManager.adapters
      True
    """

def test_suite():
    return unittest.TestSuite((
        doctest.DocTestSuite(setUp=setUp, tearDown=tearDown),
        doctest.DocTestSuite('zope.component.site'),
        doctest.DocFileSuite('README.txt',
                             setUp=setUp, tearDown=tearDown),
        doctest.DocFileSuite('socketexample.txt',
                             setUp=setUp, tearDown=tearDown),
        doctest.DocFileSuite('factory.txt',
                             setUp=setUp, tearDown=tearDown),
        ))

if __name__ == "__main__":
    unittest.main(defaultTest='test_suite')

# BBB: Import some backward-compatibility; 12/10/2004
from zope.component.bbb.tests import placelesssetup
