#!/usr/bin/env python
# vim:sw=4:et:ai

import unittest
from gaphor.UML.properties import *
from gaphor.UML.element import Element

class PropertiesTestCase(unittest.TestCase):

    def test_association_1_x(self):
        #
        # 1:-
        #
        class A(Element): pass
        class B(Element): pass

        A.one = association('one', B, 0, 1, opposite='two')
        B.two = association('two', A, 0, 1)
        a = A()
        b = B()
        a.one = b
        assert a.one is b
        assert b.two is a

    def test_association_n_x(self):
        #
        # n:-
        #
        class A(Element): pass
        class B(Element): pass
        class C(Element): pass

        A.one = association('one', B, 0, '*', opposite='two')
        B.two = association('two', A, 0, 1)

        a = A()
        b = B()
        a.one = b
        assert b in a.one
        assert b.two is a

    def test_association_1_1(self):
        #
        # 1:1
        #
        class A(Element): pass
        class B(Element): pass
        class C(Element): pass

        A.one = association('one', B, 0, 1, opposite='two')
        B.two = association('two', A, 0, 1, opposite='one')

        a = A()
        b = B()
        a.one = b
        a.one = b

        assert a.one is b
        assert b.two is a
        assert len(a._observers.get('__unlink__')) == 1
        assert len(b._observers.get('__unlink__')) == 1

        a.one = B()
        assert a.one is not b
        assert b.two is None
        assert len(a._observers.get('__unlink__')) == 1
        assert len(b._observers.get('__unlink__')) == 0

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
        assert len(a._observers.get('__unlink__')) == 0
        assert len(b._observers.get('__unlink__')) == 0

    def test_association_1_n(self):
        #
        # 1:n
        #
        class A(Element): pass
        class B(Element): pass
        class C(Element): pass

        A.one = association('one', B, lower=0, upper=1, opposite='two')
        B.two = association('two', A, lower=0, upper='*', opposite='one')

        a1 = A()
        a2 = A()
        b1 = B()
        b2 = B()

        b1.two = a1
        assert len(b1.two) == 1, 'len(b1.two) == %d' % len(b1.two)
        assert a1 in b1.two
        assert a1.one is b1, '%s/%s' % (a1.one, b1)
        b1.two = a1
        b1.two = a1
        assert len(b1.two) == 1, 'len(b1.two) == %d' % len(b1.two)
        assert a1 in b1.two
        assert a1.one is b1, '%s/%s' % (a1.one, b1)
        assert len(a1._observers.get('__unlink__')) == 1
        assert len(b1._observers.get('__unlink__')) == 1

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
        assert len(a1._observers.get('__unlink__')) == 0
        assert len(b1._observers.get('__unlink__')) == 1

        a2.one = b2

        assert len(b1.two) == 0
        assert len(b2.two) == 1
        assert a2 in b2.two
        assert a1.one is None
        assert a2.one is b2

        try:
            del b1.two[a1]
        except AttributeError:
            pass #ok
        else:
            assert 0, 'should not be removed'

    def test_association_n_n(self):
        #
        # n:n
        #
        class A(Element): pass
        class B(Element): pass
        class C(Element): pass

        A.one = association('one', B, 0, '*', opposite='two')
        B.two = association('two', A, 0, '*', opposite='one')

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
        assert len(a1._observers.get('__unlink__')) == 2
        assert len(b1._observers.get('__unlink__')) == 1

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
        assert len(a1._observers.get('__unlink__')) == 1
        assert len(b1._observers.get('__unlink__')) == 1

    def test_association_unlink(self):
        #
        # unlink
        #
        class A(Element): pass
        class B(Element): pass
        class C(Element): pass

        A.one = association('one', B, 0, '*', opposite='two')
        B.two = association('two', A, 0, '*')

        a1 = A()
        a2 = A()
        b1 = B()
        b2 = B()

        a1.one = b1
        a1.one = b2
        assert b1 in a1.one
        assert b2 in a1.one
        assert a1 in b1.two
        assert a1 in b2.two

        a2.one = b1
        assert len(a1._observers.get('__unlink__')) == 2
        assert len(b1._observers.get('__unlink__')) == 2

        # remove b1 from all elements connected to b1
        # also the signal should be removed
        b1.unlink()

        assert len(a1._observers.get('__unlink__')) == 1, a1._observers.get('__unlink__')
        #assert len(b1._observers.get('__unlink__')) == 0, b1._observers.get('__unlink__')

        assert b1 not in a1.one
        assert b2 in a1.one
        assert a1 not in b1.two
        assert a1 in b2.two

    def test_attributes(self):
        import types
        class A(Element): pass

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

    def test_enumerations(self):
        import types
        class A(Element): pass

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

    def test_notify(self):
        import types
        class A(Element):
            notified=None
            def notify(self, name, pspec):
                self.notified = name

        A.assoc = association('assoc', A)
        A.attr = attribute('attr', types.StringType, 'default')
        A.enum = enumeration('enum', ('one', 'two'), 'one')

        a = A()
        assert a.notified == None
        a.assoc = A()
        assert a.notified == 'assoc', a.notified
        a.attr = 'newval'
        assert a.notified == 'attr', a.notified
        a.enum = 'two'
        assert a.notified == 'enum', a.notified
        a.notified = None
        a.enum = 'two' # should not notify since value hasn't changed.
        assert a.notified == None

    def test_derivedunion(self):
        class A(Element): pass

        A.a = association('a', A)
        A.b = association('b', A, 0, 1)
        A.u = derivedunion('u', 0, '*', A.a, A.b)

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

        class E(Element):
            notified=False
            def notify(self, name, pspec):
                if name == 'u':
                    self.notified = True

        E.a = association('a', A)
        E.u = derivedunion('u', 0, '*', E.a)

        e = E()
        assert e.notified == False
        e.a = a
        assert e.notified == True

    def test_composite(self):
        class A(Element):
            is_unlinked = False
            def unlink(self):
                self.is_unlinked = True
                Element.unlink(self)

        A.comp = association('comp', A, composite=True, opposite='other')
        A.other = association('other', A, composite=False, opposite='comp')

        a = A()
        a.name = 'a'
        b = A()
        b.name = 'b'
        a.comp = b
        assert b in a.comp
        assert a in b.other

        a.unlink()
        assert a.is_unlinked
        assert b.is_unlinked

    def test_undo_attribute(self):
        import types
        from gaphor.services.undomanager import get_undo_manager
        undo_manager = get_undo_manager()

        class A(Element):
            attr = attribute('attr', types.StringType, default='default')

        a = A()
        assert a.attr == 'default', a.attr
        undo_manager.begin_transaction()
        a.attr = 'five'

        undo_manager.commit_transaction()
        assert a.attr == 'five'

        undo_manager.undo_transaction()
        assert a.attr == 'default', a.attr

        undo_manager.redo_transaction()
        assert a.attr == 'five'

    def test_undo_attribute(self):
        import types
        from gaphor.services.undomanager import get_undo_manager
        undo_manager = get_undo_manager()

        class A(Element): pass
        class B(Element): pass

        A.one = association('one', B, 0, 1, opposite='two')
        B.two = association('two', A, 0, 1)

        a = A()
        b = B()

        assert a.one is None
        assert b.two is None

        undo_manager.begin_transaction()
        a.one = b

        undo_manager.commit_transaction()
        assert a.one is b
        assert b.two is a

        undo_manager.undo_transaction()
        assert a.one is None
        assert b.two is None

        undo_manager.redo_transaction()
        assert a.one is b
        assert b.two is a

