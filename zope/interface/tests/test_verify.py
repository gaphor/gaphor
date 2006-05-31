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
"""Interface Verify tests

$Id$
"""
from zope.interface import Interface, implements, classImplements, Attribute
from zope.interface.verify import verifyClass, verifyObject
from zope.interface.exceptions import DoesNotImplement, BrokenImplementation
from zope.interface.exceptions import BrokenMethodImplementation

import unittest

class Test(unittest.TestCase):

    def testNotImplemented(self):

        class C(object): pass

        class I(Interface): pass

        self.assertRaises(DoesNotImplement, verifyClass, I, C)

        classImplements(C, I)

        verifyClass(I, C)

    def testMissingAttr(self):

        class I(Interface):
            def f(): pass

        class C(object):
            implements(I)

        self.assertRaises(BrokenImplementation, verifyClass, I, C)

        C.f=lambda self: None

        verifyClass(I, C)

    def testMissingAttr_with_Extended_Interface(self):

        class II(Interface):
            def f():
                pass

        class I(II):
            pass

        class C(object):
            implements(I)

        self.assertRaises(BrokenImplementation, verifyClass, I, C)

        C.f=lambda self: None

        verifyClass(I, C)

    def testWrongArgs(self):

        class I(Interface):
            def f(a): pass

        class C(object):
            def f(self, b): pass

            implements(I)

        # We no longer require names to match.
        #self.assertRaises(BrokenMethodImplementation, verifyClass, I, C)

        C.f=lambda self, a: None

        verifyClass(I, C)

        C.f=lambda self, **kw: None

        self.assertRaises(BrokenMethodImplementation, verifyClass, I, C)

        C.f=lambda self, a, *args: None

        verifyClass(I, C)

        C.f=lambda self, a, *args, **kw: None

        verifyClass(I, C)

        C.f=lambda self, *args: None

        verifyClass(I, C)

    def testExtraArgs(self):

        class I(Interface):
            def f(a): pass

        class C(object):
            def f(self, a, b): pass

            implements(I)

        self.assertRaises(BrokenMethodImplementation, verifyClass, I, C)

        C.f=lambda self, a: None

        verifyClass(I, C)

        C.f=lambda self, a, b=None: None

        verifyClass(I, C)

    def testNoVar(self):

        class I(Interface):
            def f(a, *args): pass

        class C(object):
            def f(self, a): pass

            implements(I)

        self.assertRaises(BrokenMethodImplementation, verifyClass, I, C)

        C.f=lambda self, a, *foo: None

        verifyClass(I, C)

    def testNoKW(self):

        class I(Interface):
            def f(a, **args): pass

        class C(object):
            def f(self, a): pass

            implements(I)

        self.assertRaises(BrokenMethodImplementation, verifyClass, I, C)

        C.f=lambda self, a, **foo: None

        verifyClass(I, C)

    def testModule(self):

        from zope.interface.tests.ifoo import IFoo
        from zope.interface.tests import dummy

        verifyObject(IFoo, dummy)

    def testMethodForAttr(self):
        
        class IFoo(Interface):
             foo = Attribute("The foo Attribute")


        class Foo:
             implements(IFoo)

             def foo(self):
                 pass

        verifyClass(IFoo, Foo)

    def testNonMethodForMethod(self):

        class IBar(Interface):
             def foo():
                 pass

        class Bar:
            implements(IBar)

            foo = 1

        self.assertRaises(BrokenMethodImplementation, verifyClass, IBar, Bar)
        

def test_suite():
    loader=unittest.TestLoader()
    return loader.loadTestsFromTestCase(Test)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
