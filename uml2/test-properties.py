#!/usr/bin/env python
# vim:sw=4:et

from properties import *

def test_associations():
    #
    # 1:-
    #
    class A(object): pass
    class B(object): pass
    class C(object): pass

    A.one = association('one', B, 0, 1, 'two')
    B.two = association('two', A, 0, 1)

    a = A()
    b = B()
    a.one = b
    assert a.one is b
    assert b.two is a

    #
    # n:-
    #
    class A(object): pass
    class B(object): pass
    class C(object): pass

    A.one = association('one', B, 0, infinite, 'two')
    B.two = association('two', A, 0, 1)

    a = A()
    b = B()
    a.one = b
    assert b in a.one
    assert b.two is a

    #
    # 1:1
    #
    class A(object): pass
    class B(object): pass
    class C(object): pass

    A.one = association('one', B, 0, 1, 'two')
    B.two = association('two', A, 0, 1, 'one')

    a = A()
    b = B()
    a.one = b

    assert a.one is b
    assert b.two is a
    a.one = B()
    assert a.one is not b
    assert b.two is None

    c = C()
    try:
        a.one = c
    except Exception, e:
        pass #ok print 'exception caught:', e
    else:
        assert a.one is not c

    del a.one
    assert a.one is None
    assert b.two is None

    #
    # 1:n
    #
    class A(object): pass
    class B(object): pass
    class C(object): pass

    A.one = association('one', B, 0, 1, 'two')
    B.two = association('two', A, 0, infinite, 'one')

    a1 = A()
    a2 = A()
    b1 = B()
    b2 = B()

    b1.two = a1
    assert a1 in b1.two
    assert a1.one is b1

    b1.two = a2
    assert a1 in b1.two
    assert a2 in b1.two
    assert a1.one is b1
    assert a2.one is b1

    try:
        del b1.two
    except Exception:
        pass #ok
    else:
        assert b1.two != []

    assert a1 in b1.two
    assert a2 in b1.two
    assert a1.one is b1
    assert a2.one is b1

    b1.two.remove(a1)

    assert len(b1.two) == 1
    assert a1 not in b1.two
    assert a2 in b1.two
    assert a1.one is None
    assert a2.one is b1

    a2.one = b2

    assert len(b1.two) == 0
    assert len(b2.two) == 1
    assert a2 in b2.two
    assert a1.one is None
    assert a2.one is b2

    try:
        b1.two.remove(a1)
    except AttributeError:
        pass #ok
    else:
        assert 0, 'should not be removed'
    #
    # n:n
    #
    class A(object): pass
    class B(object): pass
    class C(object): pass

    A.one = association('one', B, 0, infinite, 'two')
    B.two = association('two', A, 0, infinite, 'one')

    a1 = A()
    a2 = A()
    b1 = B()
    b2 = B()

    a1.one = b1
    assert b1 in a1.one
    assert a1 in b1.two
    assert not a2.one
    assert not b2.two

    a1.one = b2
    assert b1 in a1.one
    assert b2 in a1.one
    assert a1 in b1.two
    assert a1 in b2.two
    assert not a2.one

    a2.one = b1
    assert len(a1.one) == 2
    assert len(a2.one) == 1
    assert len(b1.two) == 2
    assert len(b2.two) == 1
    assert b1 in a1.one
    assert b2 in a1.one
    assert a1 in b1.two
    assert a1 in b2.two
    assert b1 in a2.one
    assert a2 in b1.two

    del a1.one[b1]
    assert len(a1.one) == 1
    assert len(a2.one) == 1
    assert len(b1.two) == 1
    assert len(b2.two) == 1
    assert b1 not in a1.one
    assert b2 in a1.one
    assert a1 not in b1.two
    assert a1 in b2.two
    assert b1 in a2.one
    assert a2 in b1.two

def test_attributes():
    import types
    class A(object): pass

    A.a = attribute('a', types.StringType, 'default')

    a = A()
    assert a.a == 'default'
    a.a = 'bar'
    assert a.a == 'bar'
    del a.a
    assert a.a == 'default'
    try:
        a.a = 1
    except AttributeError:
        pass #ok
    else:
        assert 0, 'should not set integer'

def test_enumerations():
    import types
    class A(object): pass

    A.a = enumeration('a', ('one', 'two', 'three'), 'one')
    a = A()
    assert a.a == 'one'
    a.a = 'two'
    assert a.a == 'two'
    a.a = 'three'
    assert a.a == 'three'
    try:
        a.a = 'four'
    except AttributeError:
        assert a.a == 'three'
    else:
        assert 0, 'a.a could not be four'
    del a.a
    assert a.a == 'one'

def test_notify():
    import types
    class A(object):
        notified=None
        def notify(self, name):
            self.notified = name

    A.assoc = association('assoc', A)
    A.attr = attribute('attr', types.StringType, 'default')
    A.enum = enumeration('enum', ('one', 'two'), 'one')

    a = A()
    assert a.notified == None
    a.assoc = A()
    assert a.notified == 'assoc'
    a.attr = 'newval'
    assert a.notified == 'attr'
    a.enum = 'two'
    assert a.notified == 'enum'
    a.notified = None
    a.enum = 'two' # should not notify
    assert a.notified == None

def test_derivedunion():
    class A(object): pass

    A.a = association('a', A)
    A.b = association('b', A, 0, 1)
    A.u = derivedunion('u', A.a, A.b)

    a = A()
    assert len(a.a) == 0, 'a.a = %s' % a.a
    assert len(a.u) == 0, 'a.u = %s' % a.u
    a.a = b = A()
    a.a = c = A()
    assert len(a.a) == 2, 'a.a = %s' % a.a
    assert b in a.a
    assert c in a.a
    assert len(a.u) == 2, 'a.u = %s' % a.u
    assert b in a.u
    assert c in a.u

    a.b = d = A()
    assert len(a.a) == 2, 'a.a = %s' % a.a
    assert b in a.a
    assert c in a.a
    assert d == a.b
    assert len(a.u) == 3, 'a.u = %s' % a.u
    assert b in a.u
    assert c in a.u
    assert d in a.u

    class E(object):
        notified=False
        def notify(self, name):
            if name == 'u':
                self.notified = True

    E.a = association('a', A)
    E.u = derivedunion('u', E.a)

    e = E()
    assert e.notified == False
    e.a = a
    assert e.notified == True

if __name__ == '__main__':
    test_associations()
    test_attributes()
    test_enumerations()
    test_notify()
    test_derivedunion()
    print 'All tests passed.'
