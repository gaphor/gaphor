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
"""ExceptionFormatter tests.

$Id$
"""
import sys
from unittest import TestCase, main, makeSuite

from zope.exceptions.exceptionformatter import format_exception
from zope.testing.cleanup import CleanUp # Base class w registry cleanup

def tb(as_html=0):
    t, v, b = sys.exc_info()
    try:
        return ''.join(format_exception(t, v, b, as_html=as_html))
    finally:
        del b


class ExceptionForTesting (Exception):
    pass



class TestingTracebackSupplement(object):

    source_url = '/somepath'
    line = 634
    column = 57
    warnings = ['Repent, for the end is nigh']

    def __init__(self, expression):
        self.expression = expression



class Test(CleanUp, TestCase):

    def testBasicNamesText(self, as_html=0):
        try:
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = tb(as_html)
            # The traceback should include the name of this function.
            self.assert_(s.find('testBasicNamesText') >= 0)
            # The traceback should include the name of the exception.
            self.assert_(s.find('ExceptionForTesting') >= 0)
        else:
            self.fail('no exception occurred')

    def testBasicNamesHTML(self):
        self.testBasicNamesText(1)

    def testSupplement(self, as_html=0):
        try:
            __traceback_supplement__ = (TestingTracebackSupplement,
                                        "You're one in a million")
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = tb(as_html)
            # The source URL
            self.assert_(s.find('/somepath') >= 0, s)
            # The line number
            self.assert_(s.find('634') >= 0, s)
            # The column number
            self.assert_(s.find('57') >= 0, s)
            # The expression
            self.assert_(s.find("You're one in a million") >= 0, s)
            # The warning
            self.assert_(s.find("Repent, for the end is nigh") >= 0, s)
        else:
            self.fail('no exception occurred')

    def testSupplementHTML(self):
        self.testSupplement(1)

    def testTracebackInfo(self, as_html=0):
        try:
            __traceback_info__ = "Adam & Eve"
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = tb(as_html)
            if as_html:
                # Be sure quoting is happening.
                self.assert_(s.find('Adam &amp; Eve') >= 0, s)
            else:
                self.assert_(s.find('Adam & Eve') >= 0, s)
        else:
            self.fail('no exception occurred')

    def testTracebackInfoHTML(self):
        self.testTracebackInfo(1)

    def testTracebackInfoTuple(self):
        try:
            __traceback_info__ = ("Adam", "Eve")
            raise ExceptionForTesting
        except ExceptionForTesting:
            s = tb()
            self.assert_(s.find('Adam') >= 0, s)
            self.assert_(s.find('Eve') >= 0, s)
        else:
            self.fail('no exception occurred')

    def testMultipleLevels(self):
        # Makes sure many levels are shown in a traceback.
        def f(n):
            """Produces a (n + 1)-level traceback."""
            __traceback_info__ = 'level%d' % n
            if n > 0:
                f(n - 1)
            else:
                raise ExceptionForTesting

        try:
            f(10)
        except ExceptionForTesting:
            s = tb()
            for n in range(11):
                self.assert_(s.find('level%d' % n) >= 0, s)
        else:
            self.fail('no exception occurred')

    def testQuoteLastLine(self):
        class C(object): pass
        try: raise TypeError, C()
        except:
            s = tb(1)
        else:
            self.fail('no exception occurred')
        self.assert_(s.find('&lt;') >= 0, s)
        self.assert_(s.find('&gt;') >= 0, s)



def test_suite():
    return makeSuite(Test)

if __name__=='__main__':
    main(defaultTest='test_suite')
