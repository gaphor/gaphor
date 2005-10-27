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
"""Documentation tests.

$Id$
"""
from unittest import TestCase, main, makeSuite

from zope.interface import Interface, Attribute

class Test(TestCase):

    def testBlech(self):
        from zope.interface.document import asStructuredText

        self.assertEqual(asStructuredText(I2), '''\
I2

 I2 doc

 This interface extends:

  o _I1

 Attributes:

  a1 -- no documentation

  a2 -- a2 doc

 Methods:

  f21() -- f21 doc

  f22() -- no documentation

  f23() -- f23 doc

''')


def test_suite():
    return makeSuite(Test)

class _I1(Interface):
    def f11(): pass
    def f12(): pass

class I2(_I1):
    "I2 doc"

    a1 = Attribute('a1')
    a2 = Attribute('a2', 'a2 doc')

    def f21(): "f21 doc"
    def f22(): pass
    def f23(): "f23 doc"

if __name__=='__main__':
    main(defaultTest='test_suite')
