#!/usr/bin/env python

from __future__ import absolute_import

import unittest
from zope import component

from gaphor.UML.element import Element
from gaphor.UML.interfaces import IAssociationChangeEvent
from gaphor.UML.properties import *
from gaphor.application import Application


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

        a.one = None
        assert a.one is None
        assert b.two is None

        a.one = b
        assert a.one is b
        assert b.two is a

        del a.one
        assert a.one is None
        assert b.two is None

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
        class A(Element):
            pass

        class B(Element):
            pass

        class C(Element):
            pass

        A.one = association('one', B, 0, 1, opposite='two')
        B.two = association('two', A, 0, 1, opposite='one')

        a = A()
        b = B()
        a.one = b
        a.one = b

        assert a.one is b
        assert b.two is a
        # assert len(a._observers.get('__unlink__')) == 0
        # assert len(b._observers.get('__unlink__')) == 0

        a.one = B()
        assert a.one is not b
        assert b.two is None
        # assert len(a._observers.get('__unlink__')) == 0
        # assert len(b._observers.get('__unlink__')) == 0

        c = C()
        try:
            a.one = c
        except Exception as e:
            pass  # ok print 'exception caught:', e
        else:
            assert a.one is not c

        del a.one
        assert a.one is None
        assert b.two is None
        # assert len(a._observers.get('__unlink__')) == 0
        # assert len(b._observers.get('__unlink__')) == 0

    def test_association_1_n(self):
        #
        # 1:n
        #
        class A(Element):
            pass

        class B(Element):
            pass

        class C(Element):
            pass

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
        # assert len(a1._observers.get('__unlink__')) == 0
        # assert len(b1._observers.get('__unlink__')) == 0

        b1.two = a2
        assert a1 in b1.two
        assert a2 in b1.two
        assert a1.one is b1
        assert a2.one is b1

        try:
            del b1.two
        except Exception:
            pass  # ok
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
        # assert len(a1._observers.get('__unlink__')) == 0
        # assert len(b1._observers.get('__unlink__')) == 0

        a2.one = b2

        assert len(b1.two) == 0
        assert len(b2.two) == 1
        assert a2 in b2.two
        assert a1.one is None
        assert a2.one is b2

        try:
            del b1.two[a1]
        except ValueError:
            pass  # ok
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
        # assert len(a1._observers.get('__unlink__')) == 0
        # assert len(b1._observers.get('__unlink__')) == 0

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
        # assert len(a1._observers.get('__unlink__')) == 0
        # assert len(b1._observers.get('__unlink__')) == 0

    def test_association_swap(self):
        class A(Element): pass

        class B(Element): pass

        class C(Element): pass

        A.one = association('one', B, 0, '*')

        a = A()
        b1 = B()
        b2 = B()

        a.one = b1
        a.one = b2
        assert a.one.size() == 2
        assert a.one[0] is b1
        assert a.one[1] is b2

        events = []

        @component.adapter(IAssociationChangeEvent)
        def handler(event, events=events):
            events.append(event)

        #        Application.register_handler(handler)
        #        try:
        a.one.swap(b1, b2)
        #            assert len(events) == 1
        #            assert events[0].property is A.one
        #            assert events[0].element is a
        #        finally:
        #            Application.unregister_handler(handler)

        assert a.one.size() == 2
        assert a.one[0] is b2
        assert a.one[1] is b1

    def test_association_unlink_1(self):
        #
        # unlink
        #
        class A(Element): pass

        class B(Element): pass

        class C(Element): pass

        A.one = association('one', B, 0, '*')

        a1 = A()
        a2 = A()
        b1 = B()
        b2 = B()

        a1.one = b1
        a1.one = b2
        assert b1 in a1.one
        assert b2 in a1.one

        a2.one = b1
        # assert len(a1._observers.get('__unlink__')) == 0
        # assert len(b1._observers.get('__unlink__')) == 0

        # remove b1 from all elements connected to b1
        # also the signal should be removed
        b1.unlink()

        # assert len(a1._observers.get('__unlink__')) == 1, a1._observers.get('__unlink__')
        # assert len(b1._observers.get('__unlink__')) == 0, b1._observers.get('__unlink__')

        assert b1 not in a1.one
        assert b2 in a1.one

    def test_association_unlink_2(self):
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
        # assert len(a1._observers.get('__unlink__')) == 0
        # assert len(b1._observers.get('__unlink__')) == 0

        # remove b1 from all elements connected to b1
        # also the signal should be removed
        b1.unlink()

        # assert len(a1._observers.get('__unlink__')) == 1, a1._observers.get('__unlink__')
        # assert len(b1._observers.get('__unlink__')) == 0, b1._observers.get('__unlink__')

        assert b1 not in a1.one
        assert b2 in a1.one
        assert a1 not in b1.two
        assert a1 in b2.two

    def test_attributes(self):
        class A(Element):
            pass

        A.a = attribute('a', bytes, 'default')

        a = A()
        assert a.a == 'default', a.a
        a.a = 'bar'
        assert a.a == 'bar', a.a
        del a.a
        assert a.a == 'default'
        try:
            a.a = 1
        except AttributeError:
            pass  # ok
        else:
            assert 0, 'should not set integer'

    def test_enumerations(self):
        class A(Element):
            pass

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

    def skiptest_notify(self):
        class A(Element):
            notified = None

            def notify(self, name, pspec):
                self.notified = name

        A.assoc = association('assoc', A)
        A.attr = attribute('attr', bytes, 'default')
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
        a.enum = 'two'  # should not notify since value hasn't changed.
        assert a.notified == None

    def test_derivedunion(self):
        class A(Element): pass

        A.a = association('a', A)
        A.b = association('b', A, 0, 1)
        A.u = derivedunion('u', object, 0, '*', A.a, A.b)

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

    def skiptest_deriveduntion_notify(self):
        class A(Element): pass

        class E(Element):
            notified = False

            def notify(self, name, pspec):
                if name == 'u':
                    self.notified = True

        E.a = association('a', A)
        E.u = derivedunion('u', A, 0, '*', E.a)

        e = E()
        assert e.notified == False
        e.a = A()
        assert e.notified == True

    def test_derivedunion_listmixins(self):
        class A(Element): pass

        A.a = association('a', A)
        A.b = association('b', A)
        A.u = derivedunion('u', A, 0, '*', A.a, A.b)
        A.name = attribute('name', str, 'default')

        a = A()
        a.a = A()
        a.a = A()
        a.b = A()
        a.a[0].name = 'foo'
        a.a[1].name = 'bar'
        a.b[0].name = 'baz'

        assert list(a.a[:].name) == ['foo', 'bar']
        assert list(a.u[:].name) == ['foo', 'bar', 'baz']

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

    def skiptest_derivedunion(self):

        class A(Element):
            is_unlinked = False

            def unlink(self):
                self.is_unlinked = True
                Element.unlink(self)

        A.a = association('a', A, upper=1)
        A.b = association('b', A)

        A.derived_a = derivedunion('derived_a', A, 0, 1, A.a)
        A.derived_b = derivedunion('derived_b', A, 0, '*', A.b)
        events = []

        @component.adapter(IAssociationChangeEvent)
        def handler(event, events=events):
            events.append(event)

        Application.register_handler(handler)
        try:
            a = A()
            a.a = A()
            assert len(events) == 2, events
            assert events[0].property is A.derived_a
            assert events[1].property is A.a
        finally:
            Application.unregister_handler(handler)

    def skiptest_derivedunion_events(self):
        from zope import component
        from gaphor.UML.event import DerivedAddEvent, DerivedDeleteEvent

        class A(Element):
            is_unlinked = False

            def unlink(self):
                self.is_unlinked = True
                Element.unlink(self)

        A.a1 = association('a1', A, upper=1)
        A.a2 = association('a2', A, upper=1)
        A.b1 = association('b1', A, upper='*')
        A.b2 = association('b2', A, upper='*')
        A.b3 = association('b3', A, upper=1)

        A.derived_a = derivedunion('derived_a', object, 0, 1, A.a1, A.a2)
        A.derived_b = derivedunion('derived_b', object, 0, '*', A.b1, A.b2, A.b3)

        events = []

        @component.adapter(IAssociationChangeEvent)
        def handler(event, events=events):
            events.append(event)

        Application.register_handler(handler)
        try:
            a = A()
            a.a1 = A()
            assert len(events) == 2
            assert events[0].property is A.derived_a
            assert events[1].property is A.a1
            assert a.derived_a is a.a1
            a.a1 = A()
            assert len(events) == 4, len(events)
            assert a.derived_a is a.a1

            a.a2 = A()
            # Should not emit DerivedSetEvent
            assert len(events) == 5, len(events)
            assert events[4].property is A.a2

            del events[:]
            old_a1 = a.a1
            del a.a1
            assert len(events) == 2, len(events)
            assert events[0].property is A.derived_a
            assert events[0].new_value is a.a2, '%s %s %s' % (a.a1, a.a2, events[3].new_value)
            assert events[0].old_value is old_a1, '%s %s %s' % (a.a1, a.a2, events[3].old_value)
            assert events[1].property is A.a1

            del events[:]
            old_a2 = a.a2
            del a.a2
            assert len(events) == 2, len(events)
            assert events[0].property is A.derived_a
            assert events[0].new_value is None, '%s %s %s' % (a.a1, a.a2, events[5].new_value)
            assert events[0].old_value is old_a2, '%s %s %s' % (a.a1, a.a2, events[5].old_value)
            assert events[1].property is A.a2

            del events[:]
            assert len(events) == 0, len(events)

            a.b1 = A()
            assert len(events) == 2
            assert events[0].property is A.derived_b
            assert events[1].property is A.b1

            a.b2 = A()
            assert len(events) == 4
            assert events[2].property is A.derived_b
            assert events[3].property is A.b2

            a.b2 = A()
            assert len(events) == 6
            assert events[4].property is A.derived_b
            assert events[5].property is A.b2

            a.b3 = A()
            assert len(events) == 8, len(events)
            assert events[6].property is A.derived_b
            assert events[7].property is A.b3

            # Add b3's value to b2, should not emit derived union event
            a.b2 = a.b3
            assert len(events) == 9, len(events)
            assert events[8].property is A.b2

            # Remove b3's value to b2
            del a.b2[a.b3]
            assert len(events) == 10, len(events)
            assert events[9].property is A.b2

            a.b3 = A()
            assert len(events) == 13, len(events)
            assert events[10].property is A.derived_b
            assert type(events[10]) is DerivedDeleteEvent, type(events[10])
            assert events[11].property is A.derived_b
            assert type(events[11]) is DerivedAddEvent, type(events[11])
            assert events[12].property is A.b3

            del a.b3
            assert len(events) == 15, len(events)
            assert events[13].property is A.derived_b
            assert type(events[13]) is DerivedDeleteEvent, type(events[10])
            assert events[14].property is A.b3
        finally:
            Application.unregister_handler(handler)

    def skiptest_redefine(self):
        from zope import component
        from gaphor.application import Application

        class A(Element):
            is_unlinked = False

            def unlink(self):
                self.is_unlinked = True
                Element.unlink(self)

        A.a = association('a', A, upper=1)

        A.a = redefine(A, 'a', A, A.a)
        events = []

        @component.adapter(IAssociationChangeEvent)
        def handler(event, events=events):
            events.append(event)

        Application.register_handler(handler)
        try:
            a = A()
            a.a = A()
            assert len(events) == 2
            assert events[0].property is A.a, events[0].property
            assert events[1].property is A.a.original, events[1].property
        finally:
            Application.unregister_handler(handler)

    def skiptest_redefine_subclass(self):
        from zope import component

        class A(Element):
            is_unlinked = False

            def unlink(self):
                self.is_unlinked = True
                Element.unlink(self)

        A.a = association('a', A, upper=1)

        class B(A):
            pass

        B.b = redefine(B, 'b', A, A.a)

        events = []

        @component.adapter(IAssociationChangeEvent)
        def handler(event, events=events):
            events.append(event)

        Application.register_handler(handler)
        try:
            a = A()
            a.a = A()
            # Only a.a changes, no B class involved
            assert len(events) == 1
            assert events[0].property is A.a, events[0].property
            # assert events[1].property is A.a.original, events[1].property
            del events[:]

            a = B()
            a.a = A()
            # Now events are sent for both association and redefine
            assert len(events) == 2
            assert events[0].property is B.b, events[0].property
            assert events[1].property is B.b.original, events[1].property
        finally:
            Application.unregister_handler(handler)


if __name__ == '__main__':
    unittest.main()

# vim:sw=4:et:ai
