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
"""Utility service tests

$Id$
"""
from unittest import TestCase, main, makeSuite
from zope.component import \
     getUtility, getUtilitiesFor, getService, queryUtility, \
     getServices, getUtilitiesFor, getGlobalServices
from zope.component.exceptions import ComponentLookupError
from zope.component.servicenames import Utilities
from zope.interface import Interface, implements

from zope.testing.cleanup import CleanUp # Base class w registry cleanup

class IDummyUtility(Interface):
    pass

class IDummerUtility(IDummyUtility):
    pass

class DummyUtility(object):
    __name__ = 'DummyUtility'
    implements(IDummyUtility)

class DummyUtility2(object):
    implements(IDummyUtility)
    __name__ = 'DummyUtility2'

    def __len__(self):
        return 0

class DummerUtility(object):
    __name__ = 'DummerUtility'
    implements(IDummerUtility)


dummyUtility = DummyUtility()
dummerUtility = DummerUtility()
dummyUtility2 = DummyUtility2()

class Test(TestCase, CleanUp):

    def setUp(self):
        from zope.component import bbb
        bbb.__warn__ = False
        bbb.service.__warn__ = False

        CleanUp.setUp(self)
        sm = getGlobalServices()
        defineService = sm.defineService
        provideService = sm.provideService
        from zope.component.interfaces import IUtilityService
        defineService('Utilities',IUtilityService)
        from zope.component.utility import GlobalUtilityService
        provideService('Utilities', GlobalUtilityService())

    def cleanUp(self):
        super(Test, self).cleanUp()
        from zope.component import bbb
        bbb.__warn__ = True
        bbb.service.__warn__ = True

    def testGetUtility(self):
        us = getService(Utilities)
        self.assertRaises(
            ComponentLookupError, getUtility, IDummyUtility)
        us.provideUtility(IDummyUtility, dummyUtility)
        self.assertEqual(getUtility(IDummyUtility), dummyUtility)

    def testQueryUtility(self):
        us = getService(Utilities)
        self.assertEqual(queryUtility(IDummyUtility), None)
        self.assertEqual(queryUtility(IDummyUtility, default=self), self)
        us.provideUtility(IDummyUtility, dummyUtility)
        self.assertEqual(queryUtility(IDummyUtility), dummyUtility)

    def testgetUtilitiesFor(self):
        us = getService(Utilities)
        us.provideUtility(IDummyUtility, dummyUtility)
        self.assertEqual(list(getUtilitiesFor(IDummyUtility)),
                         [('',dummyUtility)])
        self.assertEqual(list(us.getUtilitiesFor(IDummyUtility)),
                         [('',dummyUtility)])

    def testregistrations(self):
        us = getService(Utilities)
        us.provideUtility(IDummyUtility, dummyUtility)
        self.assertEqual(
            map(str, us.registrations()),
            ["UtilityRegistration('IDummyUtility', '', 'DummyUtility', '')"])

    def testOverrides(self):
        us = getService(Utilities)

        # fail if nothing registered:
        self.assertRaises(
            ComponentLookupError, getUtility, IDummyUtility)

        # set and retiev dummy
        us.provideUtility(IDummyUtility, dummyUtility)
        self.assertEqual(getUtility(IDummyUtility), dummyUtility)

        # dummer overrides
        us.provideUtility(IDummerUtility, dummerUtility)
        self.assertEqual(getUtility(IDummerUtility), dummerUtility)

        # But not if we ask for dummy
        self.assertEqual(getUtility(IDummyUtility), dummyUtility)

        # same for named:
        self.assertRaises(
            ComponentLookupError, getUtility, IDummyUtility, 'bob')
        us.provideUtility(IDummyUtility, dummyUtility, 'bob')
        self.assertEqual(getUtility(IDummyUtility), dummyUtility, 'bob')
        us.provideUtility(IDummerUtility, dummerUtility, 'bob')
        self.assertEqual(getUtility(IDummerUtility), dummerUtility, 'bob')
        self.assertEqual(getUtility(IDummyUtility), dummyUtility, 'bob')

        # getUtilitiesFor doesn the right thing:
        uts = list(us.getUtilitiesFor(IDummyUtility))
        uts.sort()
        self.assertEqual(uts, [('', dummyUtility), ('bob', dummyUtility)])
        uts = list(us.getUtilitiesFor(IDummerUtility))
        uts.sort()
        self.assertEqual(uts, [('', dummerUtility), ('bob', dummerUtility)])

        return us

    def test_getAllUtilitiesRegisteredFor(self):
        us = self.testOverrides()

        # getAllUtilitiesRegisteredFor includes overridden

        uts = list(us.getAllUtilitiesRegisteredFor(IDummerUtility))
        self.assertEqual(uts, [dummerUtility, dummerUtility])

        uts = list(us.getAllUtilitiesRegisteredFor(IDummyUtility))
        uts.remove(dummyUtility)
        uts.remove(dummyUtility)
        uts.remove(dummerUtility)
        uts.remove(dummerUtility)
        self.assertEqual(uts, [])


    def test_getAllUtilitiesRegisteredFor_empty(self):
        us = getService(Utilities)
        class IFoo(Interface):
            pass
        self.assertEqual(list(us.getAllUtilitiesRegisteredFor(IFoo)), [])


def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
