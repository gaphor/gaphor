##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
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
"""Global Adapter Service Tests

$Id$
"""
import unittest
from doctest import DocTestSuite

from zope.component.adapter import GlobalAdapterService

class GlobalAdapterServiceTests(unittest.TestCase):

    # This test does not work with the backward-compatibility code.
    # Global adapter services are not pickled anyways.
    def BBB_test_pickling(self):
        from zope.component.bbb.tests.test_service import testServiceManager
        from zope.component.interfaces import IAdapterService
        testServiceManager.defineService('Adapters', IAdapterService)
        adapters = GlobalAdapterService()
        testServiceManager.provideService('Adapters', adapters)
        import pickle

        as = pickle.loads(pickle.dumps(adapters))
        self.assert_(as.sm is adapters.sm)

        testServiceManager._clear()

def test_suite():
    suite = unittest.makeSuite(GlobalAdapterServiceTests)
    suite.addTest(DocTestSuite('zope.component.adapter'))
    return suite
