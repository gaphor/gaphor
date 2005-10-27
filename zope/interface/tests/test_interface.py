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
"""Test Interface implementation

$Id$
"""
import sys
import unittest
from zope.testing.doctestunit import DocTestSuite
from zope.interface.tests.unitfixtures import *  # hehehe
from zope.interface.exceptions import BrokenImplementation, Invalid
from zope.interface import implementedBy, providedBy
from zope.interface import Interface, directlyProvides, Attribute
from zope import interface

class InterfaceTests(unittest.TestCase):

    def testInterfaceSetOnAttributes(self):
        self.assertEqual(FooInterface['foobar'].interface,
                         FooInterface)
        self.assertEqual(FooInterface['aMethod'].interface,
                         FooInterface)

    def testClassImplements(self):
        self.assert_(IC.implementedBy(C))

        self.assert_(I1.implementedBy(A))
        self.assert_(I1.implementedBy(B))
        self.assert_(not I1.implementedBy(C))
        self.assert_(I1.implementedBy(D))
        self.assert_(I1.implementedBy(E))

        self.assert_(not I2.implementedBy(A))
        self.assert_(I2.implementedBy(B))
        self.assert_(not I2.implementedBy(C))

        # No longer after interfacegeddon
        # self.assert_(not I2.implementedBy(D))

        self.assert_(not I2.implementedBy(E))

    def testUtil(self):
        self.assert_(IC in implementedBy(C))
        self.assert_(I1 in implementedBy(A))
        self.assert_(not I1 in implementedBy(C))
        self.assert_(I2 in implementedBy(B))
        self.assert_(not I2 in implementedBy(C))

        self.assert_(IC in providedBy(C()))
        self.assert_(I1 in providedBy(A()))
        self.assert_(not I1 in providedBy(C()))
        self.assert_(I2 in providedBy(B()))
        self.assert_(not I2 in providedBy(C()))


    def testObjectImplements(self):
        self.assert_(IC.providedBy(C()))

        self.assert_(I1.providedBy(A()))
        self.assert_(I1.providedBy(B()))
        self.assert_(not I1.providedBy(C()))
        self.assert_(I1.providedBy(D()))
        self.assert_(I1.providedBy(E()))

        self.assert_(not I2.providedBy(A()))
        self.assert_(I2.providedBy(B()))
        self.assert_(not I2.providedBy(C()))

        # Not after interface geddon
        # self.assert_(not I2.providedBy(D()))

        self.assert_(not I2.providedBy(E()))

    def testDeferredClass(self):
        a = A()
        self.assertRaises(BrokenImplementation, a.ma)


    def testInterfaceExtendsInterface(self):
        self.assert_(BazInterface.extends(BobInterface))
        self.assert_(BazInterface.extends(BarInterface))
        self.assert_(BazInterface.extends(FunInterface))
        self.assert_(not BobInterface.extends(FunInterface))
        self.assert_(not BobInterface.extends(BarInterface))
        self.assert_(BarInterface.extends(FunInterface))
        self.assert_(not BarInterface.extends(BazInterface))

    def testVerifyImplementation(self):
        from zope.interface.verify import verifyClass
        self.assert_(verifyClass(FooInterface, Foo))
        self.assert_(Interface.providedBy(I1))

    def test_names(self):
        names = list(_I2.names()); names.sort()
        self.assertEqual(names, ['f21', 'f22', 'f23'])
        names = list(_I2.names(all=True)); names.sort()
        self.assertEqual(names, ['a1', 'f11', 'f12', 'f21', 'f22', 'f23'])

    def test_namesAndDescriptions(self):
        names = [nd[0] for nd in _I2.namesAndDescriptions()]; names.sort()
        self.assertEqual(names, ['f21', 'f22', 'f23'])
        names = [nd[0] for nd in _I2.namesAndDescriptions(1)]; names.sort()
        self.assertEqual(names, ['a1', 'f11', 'f12', 'f21', 'f22', 'f23'])

        for name, d in _I2.namesAndDescriptions(1):
            self.assertEqual(name, d.__name__)

    def test_getDescriptionFor(self):
        self.assertEqual(_I2.getDescriptionFor('f11').__name__, 'f11')
        self.assertEqual(_I2.getDescriptionFor('f22').__name__, 'f22')
        self.assertEqual(_I2.queryDescriptionFor('f33', self), self)
        self.assertRaises(KeyError, _I2.getDescriptionFor, 'f33')

    def test___getitem__(self):
        self.assertEqual(_I2['f11'].__name__, 'f11')
        self.assertEqual(_I2['f22'].__name__, 'f22')
        self.assertEqual(_I2.get('f33', self), self)
        self.assertRaises(KeyError, _I2.__getitem__, 'f33')

    def test___contains__(self):
        self.failUnless('f11' in _I2)
        self.failIf('f33' in _I2)

    def test___iter__(self):
        names = list(iter(_I2))
        names.sort()
        self.assertEqual(names, ['a1', 'f11', 'f12', 'f21', 'f22', 'f23'])

    def testAttr(self):
        description = _I2.getDescriptionFor('a1')
        self.assertEqual(description.__name__, 'a1')
        self.assertEqual(description.__doc__, 'This is an attribute')

    def testFunctionAttributes(self):
        # Make sure function attributes become tagged values.
        meth = _I1['f12']
        self.assertEqual(meth.getTaggedValue('optional'), 1)

    def testInvariant(self):
        # set up
        o = InvariantC()
        directlyProvides(o, IInvariant)
        # a helper
        def errorsEqual(self, o, error_len, error_msgs, interface=None):
            if interface is None:
                interface = IInvariant
            self.assertRaises(Invalid, interface.validateInvariants, o)
            e = []
            try:
                interface.validateInvariants(o, e)
            except Invalid, error:
                self.assertEquals(error.args[0], e)
            else:
                self._assert(0) # validateInvariants should always raise 
                # Invalid
            self.assertEquals(len(e), error_len)
            msgs = [error.args[0] for error in e]
            msgs.sort()
            for msg in msgs:
                self.assertEquals(msg, error_msgs.pop(0))
        # the tests
        self.assertEquals(IInvariant.getTaggedValue('invariants'), 
                          [ifFooThenBar])
        self.assertEquals(IInvariant.validateInvariants(o), None)
        o.bar = 27
        self.assertEquals(IInvariant.validateInvariants(o), None)
        o.foo = 42
        self.assertEquals(IInvariant.validateInvariants(o), None)
        del o.bar
        errorsEqual(self, o, 1, ['If Foo, then Bar!'])
        # nested interfaces with invariants:
        self.assertEquals(ISubInvariant.getTaggedValue('invariants'), 
                          [BarGreaterThanFoo])
        o = InvariantC()
        directlyProvides(o, ISubInvariant)
        o.foo = 42
        # even though the interface has changed, we should still only have one 
        # error.
        errorsEqual(self, o, 1, ['If Foo, then Bar!'], ISubInvariant)
        # however, if we set foo to 0 (Boolean False) and bar to a negative 
        # number then we'll get the new error
        o.foo = 2
        o.bar = 1
        errorsEqual(self, o, 1, ['Please, Boo MUST be greater than Foo!'], 
                    ISubInvariant)
        # and if we set foo to a positive number and boo to 0, we'll
        # get both errors!
        o.foo = 1
        o.bar = 0
        errorsEqual(self, o, 2, ['If Foo, then Bar!',
                                 'Please, Boo MUST be greater than Foo!'],
                    ISubInvariant)
        # for a happy ending, we'll make the invariants happy
        o.foo = 1
        o.bar = 2
        self.assertEquals(IInvariant.validateInvariants(o), None) # woohoo
        # now we'll do two invariants on the same interface, 
        # just to make sure that a small
        # multi-invariant interface is at least minimally tested.
        o = InvariantC()
        directlyProvides(o, IInvariant)
        o.foo = 42
        old_invariants = IInvariant.getTaggedValue('invariants')
        invariants = old_invariants[:]
        invariants.append(BarGreaterThanFoo) # if you really need to mutate,
        # then this would be the way to do it.  Probably a bad idea, though. :-)
        IInvariant.setTaggedValue('invariants', invariants)
        #
        # even though the interface has changed, we should still only have one 
        # error.
        errorsEqual(self, o, 1, ['If Foo, then Bar!'])
        # however, if we set foo to 0 (Boolean False) and bar to a negative 
        # number then we'll get the new error
        o.foo = 2
        o.bar = 1
        errorsEqual(self, o, 1, ['Please, Boo MUST be greater than Foo!'])
        # and if we set foo to a positive number and boo to 0, we'll
        # get both errors!
        o.foo = 1
        o.bar = 0
        errorsEqual(self, o, 2, ['If Foo, then Bar!',
                                 'Please, Boo MUST be greater than Foo!'])
        # for another happy ending, we'll make the invariants happy again
        o.foo = 1
        o.bar = 2
        self.assertEquals(IInvariant.validateInvariants(o), None) # bliss
        # clean up
        IInvariant.setTaggedValue('invariants', old_invariants)

    def test___doc___element(self):
        class I(Interface):
            "xxx"

        self.assertEqual(I.__doc__, "xxx")
        self.assertEqual(list(I), [])

        class I(Interface):
            "xxx"

            __doc__ = Attribute('the doc')

        self.assertEqual(I.__doc__, "")
        self.assertEqual(list(I), ['__doc__'])

    def testIssue228(self):
        # Test for http://collector.zope.org/Zope3-dev/228
        class I(Interface):
            "xxx"
        class Bad:
            __providedBy__ = None
        # Old style classes don't have a '__class__' attribute
        self.failUnlessRaises(AttributeError, I.providedBy, Bad)


class _I1(Interface):

    a1 = Attribute("This is an attribute")

    def f11(): pass
    def f12(): pass
    f12.optional = 1

class _I1_(_I1): pass
class _I1__(_I1_): pass

class _I2(_I1__):
    def f21(): pass
    def f22(): pass
    f23 = f22



if sys.version_info >= (2, 4):
    def test_invariant_as_decorator():
        """Invaiants can be deined in line

          >>> class IRange(interface.Interface):
          ...     min = interface.Attribute("Lower bound")
          ...     max = interface.Attribute("Upper bound")
          ...
          ...     @interface.invariant
          ...     def range_invariant(ob):
          ...         if ob.max < ob.min:
          ...             raise Invalid('max < min')


          >>> class Range(object):
          ...     interface.implements(IRange)
          ...
          ...     def __init__(self, min, max):
          ...         self.min, self.max = min, max

          >>> IRange.validateInvariants(Range(1,2))
          >>> IRange.validateInvariants(Range(1,1))
          >>> IRange.validateInvariants(Range(2,1))
          Traceback (most recent call last):
          ...
          Invalid: max < min


        """


def test_suite():
    from zope.testing import doctest
    suite = unittest.makeSuite(InterfaceTests)
    suite.addTest(doctest.DocTestSuite("zope.interface.interface"))
    if sys.version_info >= (2, 4):
        suite.addTest(doctest.DocTestSuite())
    suite.addTest(doctest.DocFileSuite(
        '../README.txt',
        globs={'__name__': '__main__'},
        optionflags=doctest.NORMALIZE_WHITESPACE,
        ))
    suite.addTest(doctest.DocFileSuite(
        '../README.ru.txt',
        globs={'__name__': '__main__'},
        optionflags=doctest.NORMALIZE_WHITESPACE,
        ))
    return suite

def main():
    unittest.TextTestRunner().run(test_suite())

if __name__=="__main__":
    main()
