from __future__ import annotations

from typing import List, Optional

from gaphor.core import event_handler
from gaphor.core.modeling import Element
from gaphor.core.modeling.event import AssociationUpdated
from gaphor.core.modeling.properties import (
    association,
    attribute,
    derivedunion,
    enumeration,
    redefine,
    relation_many,
    relation_one,
)


def test_association_1_x():
    #
    # 1:-
    #
    class A(Element):
        one: relation_one[Optional[B]]

    class B(Element):
        two: relation_one[A]

    A.one = association("one", B, 0, 1, opposite="two")
    B.two = association("two", A, 0, 1)
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


def test_association_n_x():
    #
    # n:-
    #
    class A(Element):
        one: relation_many[B]

    class B(Element):
        two: relation_one[A]

    A.one = association("one", B, 0, "*", opposite="two")
    B.two = association("two", A, 0, 1)

    a = A()
    b = B()
    a.one = b
    assert b in a.one
    assert b.two is a


def test_association_1_1():
    #
    # 1:1
    #
    class A(Element):
        one: relation_one[B]

    class B(Element):
        two: relation_one[A]

    class C(Element):
        pass

    A.one = association("one", B, 0, 1, opposite="two")
    B.two = association("two", A, 0, 1, opposite="one")

    a = A()
    b = B()
    a.one = b
    a.one = b

    assert a.one is b
    assert b.two is a

    a.one = B()
    assert a.one is not b
    assert b.two is None

    c = C()
    try:
        a.one = c
    except Exception:
        pass
    else:
        assert a.one is not c

    del a.one
    assert a.one is None
    assert b.two is None


def test_association_1_n():
    #
    # 1:n
    #
    class A(Element):
        one: relation_one[B]

    class B(Element):
        two: relation_many[A]

    class C(Element):
        pass

    A.one = association("one", B, lower=0, upper=1, opposite="two")
    B.two = association("two", A, lower=0, upper="*", opposite="one")

    a1 = A()
    a2 = A()
    b1 = B()
    b2 = B()

    b1.two = a1
    assert len(b1.two) == 1, "len(b1.two) == %d" % len(b1.two)
    assert a1 in b1.two
    assert a1.one is b1, f"{a1.one}/{b1}"
    b1.two = a1
    b1.two = a1
    assert len(b1.two) == 1, "len(b1.two) == %d" % len(b1.two)
    assert a1 in b1.two
    assert a1.one is b1, f"{a1.one}/{b1}"

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

    a2.one = b2

    assert len(b1.two) == 0
    assert len(b2.two) == 1
    assert a2 in b2.two
    assert a1.one is None
    assert a2.one is b2

    del b1.two[a1]


def test_association_n_n():
    #
    # n:n
    #
    class A(Element):
        one: relation_many[B]

    class B(Element):
        two: relation_many[A]

    class C(Element):
        pass

    A.one = association("one", B, 0, "*", opposite="two")
    B.two = association("two", A, 0, "*", opposite="one")

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


def test_association_swap():
    class A(Element):
        one: relation_many[B]

    class B(Element):
        pass

    class C(Element):
        pass

    A.one = association("one", B, 0, "*")

    a = A()
    b1 = B()
    b2 = B()

    a.one = b1
    a.one = b2
    assert a.one.size() == 2
    assert a.one[0] is b1
    assert a.one[1] is b2

    events: List[object] = []

    @event_handler(AssociationUpdated)
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


def test_association_unlink_1():
    #
    # unlink
    #
    class A(Element):
        one: relation_many[B]

    class B(Element):
        pass

    class C(Element):
        pass

    A.one = association("one", B, 0, "*")

    a1 = A()
    a2 = A()
    b1 = B()
    b2 = B()

    a1.one = b1
    a1.one = b2
    assert b1 in a1.one
    assert b2 in a1.one

    a2.one = b1

    # remove b1 from all elements connected to b1
    # also the signal should be removed
    b1.unlink()

    assert b1 not in a1.one
    assert b2 in a1.one


def test_association_unlink_2():
    #
    # unlink
    #
    class A(Element):
        one: relation_many[B]

    class B(Element):
        two: relation_many[A]

    class C(Element):
        pass

    A.one = association("one", B, 0, "*", opposite="two")
    B.two = association("two", A, 0, "*")

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

    # remove b1 from all elements connected to b1
    # also the signal should be removed
    b1.unlink()

    assert b1 not in a1.one
    assert b2 in a1.one
    assert a1 not in b1.two
    assert a1 in b2.two


def test_attributes():
    class A(Element):
        a: attribute[str]

    A.a = attribute("a", str, "default")

    a = A()
    assert a.a == "default", a.a
    a.a = "bar"
    assert a.a == "bar", a.a
    del a.a
    assert a.a == "default"
    try:
        a.a = 1
    except AttributeError:
        pass  # ok
    else:
        assert 0, "should not set integer"


def test_enumerations():
    class A(Element):
        a: enumeration

    A.a = enumeration("a", ("one", "two", "three"), "one")
    a = A()
    assert a.a == "one"
    a.a = "two"
    assert a.a == "two"
    a.a = "three"
    assert a.a == "three"
    try:
        a.a = "four"
    except AttributeError:
        assert a.a == "three"
    else:
        assert 0, "a.a could not be four"
    del a.a
    assert a.a == "one"


def test_derivedunion():
    class A(Element):
        a: relation_many[A]
        b: relation_one[A]
        u: relation_many[A]

    A.a = association("a", A)
    A.b = association("b", A, 0, 1)
    A.u = derivedunion(A, "u", object, 0, "*", A.a, A.b)

    a = A()
    assert len(a.a) == 0, f"a.a = {a.a}"
    assert len(a.u) == 0, f"a.u = {a.u}"
    a.a = b = A()
    a.a = c = A()
    assert len(a.a) == 2, f"a.a = {a.a}"
    assert b in a.a
    assert c in a.a
    assert len(a.u) == 2, f"a.u = {a.u}"
    assert b in a.u
    assert c in a.u

    a.b = d = A()
    assert len(a.a) == 2, f"a.a = {a.a}"
    assert b in a.a
    assert c in a.a
    assert d == a.b
    assert len(a.u) == 3, f"a.u = {a.u}"
    assert b in a.u
    assert c in a.u
    assert d in a.u


def test_derivedunion_notify_for_single_derived_property():
    class A(Element):
        pass

    class E(Element):
        notified = False

        a: relation_many[A]
        u: relation_many[A]

        def handle(self, event):
            if event.property is E.u:
                self.notified = True

    E.a = association("a", A)
    E.u = derivedunion(E, "u", A, 0, "*", E.a)

    e = E()
    e.a = A()

    assert e.notified is True


def test_derivedunion_notify_for_multiple_derived_properties():
    class A(Element):
        pass

    class E(Element):
        notified = False

        a: relation_many[A]
        aa: relation_many[A]
        u: relation_many[A]

        def handle(self, event):
            if event.property is E.u:
                self.notified = True

    E.a = association("a", A)
    E.aa = association("aa", A)
    E.u = derivedunion(E, "u", A, 0, "*", E.a, E.aa)

    e = E()
    e.a = A()

    assert e.notified is True


def test_derivedunion_listmixins():
    class A(Element):
        a: relation_many[A]
        b: relation_many[A]
        u: relation_many[A]
        name: attribute[str]

    A.a = association("a", A)
    A.b = association("b", A)
    A.u = derivedunion(A, "u", A, 0, "*", A.a, A.b)
    A.name = attribute("name", str, "default")

    a = A()
    a.a = A()
    a.a = A()
    a.b = A()
    a.a[0].name = "foo"
    a.a[1].name = "bar"
    a.b[0].name = "baz"

    assert list(a.a[:].name) == ["foo", "bar"]  # type: ignore[attr-defined]
    assert sorted(list(a.u[:].name)) == ["bar", "baz", "foo"]  # type: ignore[attr-defined]


def test_composite():
    class A(Element):
        is_unlinked = False
        name: str
        comp: relation_many[A]
        other: relation_many[A]

        def unlink(self):
            self.is_unlinked = True
            Element.unlink(self)

    A.comp = association("comp", A, composite=True, opposite="other")
    A.other = association("other", A, composite=False, opposite="comp")

    a = A()
    a.name = "a"
    b = A()
    b.name = "b"
    a.comp = b
    assert b in a.comp
    assert a in b.other

    a.unlink()
    assert a.is_unlinked
    assert b.is_unlinked
