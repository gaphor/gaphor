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
"""Unit Test Fixtures

$Id$
"""
from zope.interface import Interface, invariant
from zope.interface.interface import Attribute
from zope.interface.exceptions import Invalid

class mytest(Interface):
    pass

class C(object):
    def m1(self, a, b):
        "return 1"
        return 1

    def m2(self, a, b):
        "return 2"
        return 2

# testInstancesOfClassImplements

#  YAGNI IC=Interface.impliedInterface(C)
class IC(Interface):
    def m1(a, b):
        "return 1"

    def m2(a, b):
        "return 2"



C.__implemented__=IC

class I1(Interface):
    def ma():
        "blah"

class I2(I1): pass

class I3(Interface): pass

class I4(Interface): pass

class A(I1.deferred()):
    __implemented__=I1

class B(object):
    __implemented__=I2, I3

class D(A, B): pass

class E(A, B):
    __implemented__ = A.__implemented__, C.__implemented__


class FooInterface(Interface):
    """ This is an Abstract Base Class """

    foobar = Attribute("fuzzed over beyond all recognition")

    def aMethod(foo, bar, bingo):
        """ This is aMethod """

    def anotherMethod(foo=6, bar="where you get sloshed", bingo=(1,3,)):
        """ This is anotherMethod """

    def wammy(zip, *argues):
        """ yadda yadda """

    def useless(**keywords):
        """ useless code is fun! """

class Foo(object):
    """ A concrete class """

    __implemented__ = FooInterface,

    foobar = "yeah"

    def aMethod(self, foo, bar, bingo):
        """ This is aMethod """
        return "barf!"

    def anotherMethod(self, foo=6, bar="where you get sloshed", bingo=(1,3,)):
        """ This is anotherMethod """
        return "barf!"

    def wammy(self, zip, *argues):
        """ yadda yadda """
        return "barf!"

    def useless(self, **keywords):
        """ useless code is fun! """
        return "barf!"

foo_instance = Foo()

class Blah(object):
    pass

new = Interface.__class__
FunInterface = new('FunInterface')
BarInterface = new('BarInterface', [FunInterface])
BobInterface = new('BobInterface')
BazInterface = new('BazInterface', [BobInterface, BarInterface])

# fixtures for invariant tests
def ifFooThenBar(obj):
    if getattr(obj, 'foo', None) and not getattr(obj, 'bar', None):
        raise Invalid('If Foo, then Bar!')
class IInvariant(Interface):
    foo = Attribute('foo')
    bar = Attribute('bar; must eval to Boolean True if foo does')
    invariant(ifFooThenBar)
def BarGreaterThanFoo(obj):
    foo = getattr(obj, 'foo', None)
    bar = getattr(obj, 'bar', None)
    if foo is not None and isinstance(foo, type(bar)):
        # type checking should be handled elsewhere (like, say, 
        # schema); these invariants should be intra-interface 
        # constraints.  This is a hacky way to do it, maybe, but you
        # get the idea
        if not bar > foo:
            raise Invalid('Please, Boo MUST be greater than Foo!')
class ISubInvariant(IInvariant):
    invariant(BarGreaterThanFoo)
class InvariantC(object):
    pass
