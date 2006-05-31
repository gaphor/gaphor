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
"""Test interface declarations against ExtensionClass-like classes.

These tests are to make sure we do something sane in the presense of
classic ExtensionClass classes and instances.

$Id$
"""
import unittest, odd
from zope.interface import Interface, implements, implementsOnly
from zope.interface import directlyProvides, providedBy, directlyProvidedBy
from zope.interface import classImplements, classImplementsOnly, implementedBy

class I1(Interface): pass
class I2(Interface): pass
class I3(Interface): pass
class I31(I3): pass
class I4(Interface): pass
class I5(Interface): pass

class Odd(object): __metaclass__ = odd.MetaClass

class B(Odd): __implemented__ = I2


# TODO: We are going to need more magic to make classProvides work with odd
#       classes. This will work in the next iteration. For now, we'll use
#       a different mechanism.

# from zope.interface import classProvides

class A(Odd):
    implements(I1)

class C(A, B):
    implements(I31)


class Test(unittest.TestCase):

    def test_ObjectSpecification(self):
        c = C()
        directlyProvides(c, I4)
        self.assertEqual([i.getName() for i in providedBy(c)],
                         ['I4', 'I31', 'I1', 'I2']
                         )
        self.assertEqual([i.getName() for i in providedBy(c).flattened()],
                         ['I4', 'I31', 'I3', 'I1', 'I2', 'Interface']
                         )
        self.assert_(I1 in providedBy(c))
        self.failIf(I3 in providedBy(c))
        self.assert_(providedBy(c).extends(I3))
        self.assert_(providedBy(c).extends(I31))
        self.failIf(providedBy(c).extends(I5))

        class COnly(A, B):
            implementsOnly(I31)

        class D(COnly):
            implements(I5)

        classImplements(D, I5)

        c = D()
        directlyProvides(c, I4)
        self.assertEqual([i.getName() for i in providedBy(c)],
                         ['I4', 'I5', 'I31'])
        self.assertEqual([i.getName() for i in providedBy(c).flattened()],
                         ['I4', 'I5', 'I31', 'I3', 'Interface'])
        self.failIf(I1 in providedBy(c))
        self.failIf(I3 in providedBy(c))
        self.assert_(providedBy(c).extends(I3))
        self.failIf(providedBy(c).extends(I1))
        self.assert_(providedBy(c).extends(I31))
        self.assert_(providedBy(c).extends(I5))

        class COnly(A, B): __implemented__ = I31
        class D(COnly):
            implements(I5)

        classImplements(D, I5)
        c = D()
        directlyProvides(c, I4)
        self.assertEqual([i.getName() for i in providedBy(c)],
                         ['I4', 'I5', 'I31'])
        self.assertEqual([i.getName() for i in providedBy(c).flattened()],
                         ['I4', 'I5', 'I31', 'I3', 'Interface'])
        self.failIf(I1 in providedBy(c))
        self.failIf(I3 in providedBy(c))
        self.assert_(providedBy(c).extends(I3))
        self.failIf(providedBy(c).extends(I1))
        self.assert_(providedBy(c).extends(I31))
        self.assert_(providedBy(c).extends(I5))

    def test_classImplements(self):
        class A(Odd):
          implements(I3)

        class B(Odd):
          implements(I4)

        class C(A, B):
          pass
        classImplements(C, I1, I2)
        self.assertEqual([i.getName() for i in implementedBy(C)],
                         ['I1', 'I2', 'I3', 'I4'])
        classImplements(C, I5)
        self.assertEqual([i.getName() for i in implementedBy(C)],
                         ['I1', 'I2', 'I5', 'I3', 'I4'])

    def test_classImplementsOnly(self):
        class A(Odd):
            implements(I3)

        class B(Odd):
            implements(I4)

        class C(A, B):
          pass
        classImplementsOnly(C, I1, I2)
        self.assertEqual([i.__name__ for i in implementedBy(C)],
                         ['I1', 'I2'])


    def test_directlyProvides(self):
        class IA1(Interface): pass
        class IA2(Interface): pass
        class IB(Interface): pass
        class IC(Interface): pass
        class A(Odd):
            implements(IA1, IA2)

        class B(Odd):
            implements(IB)

        class C(A, B):
            implements(IC)


        ob = C()
        directlyProvides(ob, I1, I2)
        self.assert_(I1 in providedBy(ob))
        self.assert_(I2 in providedBy(ob))
        self.assert_(IA1 in providedBy(ob))
        self.assert_(IA2 in providedBy(ob))
        self.assert_(IB in providedBy(ob))
        self.assert_(IC in providedBy(ob))

        directlyProvides(ob, directlyProvidedBy(ob)-I2)
        self.assert_(I1 in providedBy(ob))
        self.failIf(I2 in providedBy(ob))
        self.failIf(I2 in providedBy(ob))
        directlyProvides(ob, directlyProvidedBy(ob), I2)
        self.assert_(I2 in providedBy(ob))

    def test_directlyProvides_fails_for_odd_class(self):
        self.assertRaises(TypeError, directlyProvides, C, I5)

    # see above
    def XXX_test_classProvides_fails_for_odd_class(self):
        try:
            class A(Odd):
                classProvides(I1)
        except TypeError:
            pass # Sucess
        self.assert_(False,
                     "Shouldn't be able to use directlyProvides on odd class."
                     )

    def test_implementedBy(self):
        class I2(I1): pass

        class C1(Odd):
          implements(I2)

        class C2(C1):
          implements(I3)

        self.assertEqual([i.getName() for i in implementedBy(C2)],
                         ['I3', 'I2'])




def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test))
    return suite


if __name__ == '__main__':
    unittest.main()
