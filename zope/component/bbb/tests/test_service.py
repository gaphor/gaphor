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
"""Test ServiceService component

$Id$
"""

import unittest
import pickle
from zope.interface import Interface, implements

from zope.exceptions import DuplicationError
from zope.testing.cleanup import CleanUp

from zope.component import getServiceDefinitions, getService, getGlobalServices
from zope.component.service import UndefinedService, InvalidService
from zope.component.service import GlobalServiceManager, GlobalService
from zope.component.exceptions import ComponentLookupError
from zope.component.interfaces import IServiceService

class IOne(Interface):
    pass

class ITwo(Interface):
    pass

class ServiceOne(GlobalService):
    implements(IOne)

class ServiceTwo(GlobalService):
    implements(ITwo)

class Test(CleanUp, unittest.TestCase):

    def setUp(self):
        super(Test, self).setUp()
        from zope.component import bbb
        bbb.__warn__ = False
        bbb.service.__warn__ = False

    def tearDown(self):
        super(Test, self).cleanUp()
        # Make sure that the testServiceManager is clean
        global testServiceManager
        testServiceManager.sm.__init__(testServiceManager.sm.__name__)
        from zope.component import bbb
        bbb.__warn__ = True
        bbb.service.__warn__ = True

    def testNormal(self):
        ss = getGlobalServices()
        ss.defineService('one', IOne)
        c = ServiceOne()
        ss.provideService('one', c)
        self.assertEqual(id(getService('one',)), id(c))

    def testFailedLookup(self):
        self.assertRaises(ComponentLookupError, getService, 'two')

    def testDup(self):
        getGlobalServices().defineService('one', IOne)
        self.assertRaises(DuplicationError,
                          getGlobalServices().defineService,
                          'one', ITwo)

        c = ServiceOne()
        getGlobalServices().provideService('one', c)

        c2 = ServiceOne()
        self.assertRaises(DuplicationError,
                          getGlobalServices().provideService,
                          'one', c2)

        self.assertEqual(id(getService('one')), id(c))


    def testUndefined(self):
        c = ServiceOne()
        self.assertRaises(UndefinedService,
                          getGlobalServices().provideService,
                          'one', c)

    def testInvalid(self):
        getGlobalServices().defineService('one', IOne)
        getGlobalServices().defineService('two', ITwo)
        c = ServiceOne()
        self.assertRaises(InvalidService,
                          getGlobalServices().provideService,
                          'two', c)

    def testGetService(self):
        # Testing looking up a service from a service manager container that
        # doesn't have a service manager.
        getGlobalServices().defineService('one', IOne)
        c = ServiceOne()
        getGlobalServices().provideService('one', c)
        self.assertEqual(id(getService('one')), id(c))

    def testGetServiceDefinitions(self):
        # test that the service definitions are the ones we added
        sm = getGlobalServices()
        sm.defineService('one', IOne)
        c = ServiceOne()
        sm.provideService('one', c)

        sm.defineService('two', ITwo)
        d = ServiceTwo()
        sm.provideService('two', d)
        defs = getServiceDefinitions()
        defs.sort()
        self.assertEqual(defs,
            [('Services', IServiceService), ('one', IOne), ('two', ITwo)])

    def testPickling(self):
        self.assertEqual(testServiceManager.__reduce__(), 'testServiceManager')
        sm = pickle.loads(pickle.dumps(testServiceManager))
        self.assert_(sm is testServiceManager)

        s2 = ServiceTwo()
        sm.defineService('2', ITwo)
        sm.provideService('2', s2)

        self.assert_(s2.__parent__ is sm)
        self.assertEqual(s2.__name__, '2')

        s = pickle.loads(pickle.dumps(s2))
        self.assert_(s is s2)
        testServiceManager._clear()

from zope.component import bbb
bbb.service.__warn__ = False
testServiceManager = GlobalServiceManager('testServiceManager', __name__)
bbb.service.__warn__ = True


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(Test),
                           ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
