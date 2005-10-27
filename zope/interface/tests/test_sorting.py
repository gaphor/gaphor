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
"""Test interface sorting

$Id$
"""

from unittest import TestCase, TestSuite, main, makeSuite

from zope.interface import Interface

class I1(Interface): pass
class I2(I1): pass
class I3(I1): pass
class I4(Interface): pass
class I5(I4): pass
class I6(I2): pass


class Test(TestCase):

    def test(self):
        l = [I1, I3, I5, I6, I4, I2]
        l.sort()
        self.assertEqual(l, [I1, I2, I3, I4, I5, I6])

    def test_w_None(self):
        l = [I1, None, I3, I5, None, I6, I4, I2]
        l.sort()
        self.assertEqual(l, [I1, I2, I3, I4, I5, I6, None, None])

def test_suite():
    return TestSuite((
        makeSuite(Test),
        ))

if __name__=='__main__':
    main(defaultTest='test_suite')
