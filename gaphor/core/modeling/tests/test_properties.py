from __future__ import annotations

import pytest

from gaphor.core import event_handler
from gaphor.core.modeling import Element
from gaphor.core.modeling.collection import collectionlist
from gaphor.core.modeling.event import AssociationUpdated
from gaphor.core.modeling.properties import (
    association,
    attribute,
    derived,
    derivedunion,
    enumeration,
    relation_many,
    relation_one,
)


def test_association_1_x():
    #
    # 1:-
    #
    class A(Element):
        one: relation_one[B | None]

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


def test_association_n_1():
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


def test_reassign_association_n_1():
    class A(Element):
        many: relation_many[B]

    class B(Element):
        one: relation_one[A]

    A.many = association("many", B, 0, "*", opposite="one")
    B.one = association("one", A, 0, 1, opposite="many")
    a = A()
    aa = A()
    b = B()
    a.many = b
    aa.many = b
    assert b in aa.many
    assert not a.many
    assert b.one is aa


def test_association_load_does_not_steal_references():
    class A(Element):
        many: relation_many[B]

    class B(Element):
        one: relation_one[A]

    A.many = association("many", B, 0, "*", opposite="one")
    B.one = association("one", A, 0, 1, opposite="many")
    a = A()
    aa = A()
    b = B()
    a.many = b

    A.many.load(aa, b)

    assert b in a.many
    assert not aa.many
    assert b.one is a


def test_association_1_1():
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

    with pytest.raises(TypeError):
        a.one = c

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
    """Test association n:n."""

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

    events: list[object] = []

    @event_handler(AssociationUpdated)
    def handler(event, events=events):
        events.append(event)

    a.one.swap(b1, b2)

    assert a.one.size() == 2
    assert a.one[0] is b2
    assert a.one[1] is b1


def test_association_unlink_1():
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


def test_can_not_set_association_to_owner(element_factory, event_manager):
    class A(Element):
        pass

    A.a = association("a", A, upper=1)

    a = element_factory.create(A)

    with pytest.raises(TypeError):
        a.a = a


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

    with pytest.raises(TypeError):
        a.a = 1


def test_attributes_loading_failure():
    class A(Element):
        a: attribute[int]

    A.a = attribute("a", int, 0)

    a = A()

    with pytest.raises(TypeError):
        A.a.load(a, "not-int")


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

    with pytest.raises(TypeError):
        a.a = "four"

    assert a.a == "three"

    del a.a
    assert a.a == "one"


def test_derived():
    class A(Element):
        a: relation_many[A]

    A.a = derived("a", str, 0, "*", lambda self: ["a", "b", "c"])

    a = A()

    assert isinstance(a.a, collectionlist)
    assert a.a == ["a", "b", "c"]


def test_derived_single_properties():
    class A(Element):
        pass

    class E(Element):
        notified = attribute("notified", int)
        a: relation_one[A]
        u: relation_one[A]

        def handle(self, event):
            if event.property is E.u:
                self.notified = True

    E.a = association("a", A, upper=1)
    E.u = derived("u", A, 0, 1, lambda self: [self.a], E.a)

    e = E()
    e.a = A()

    assert e.a is e.u
    assert e.notified


def test_derived_multi_properties():
    class A(Element):
        pass

    class E(Element):
        notified = attribute("notified", int)
        a: relation_one[A]
        b: relation_many[A]
        u: relation_many[A]

        def handle(self, event):
            if event.property is E.u:
                self.notified = True

    E.a = association("a", A, upper=1)
    E.b = association("b", A)
    E.u = derived("u", A, 0, "*", lambda self: {self.a, *self.b}, E.a, E.b)

    e = E()
    e.a = A()
    e.b = A()

    assert e.a in e.u
    assert e.b[0] in e.u
    assert e.notified


def test_derivedunion():
    class A(Element):
        a: relation_many[A]
        b: relation_one[A]
        u: relation_many[A]

    A.a = association("a", A)
    A.b = association("b", A, 0, 1)
    A.u = derivedunion("u", object, 0, "*", A.a, A.b)

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
    E.u = derivedunion("u", A, 0, "*", E.a)

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
    E.u = derivedunion("u", A, 0, "*", E.a, E.aa)

    e = E()
    e.a = A()

    assert e.notified is True


def test_derivedunion_notify_for_single_and_multi_derived_properties():
    class A(Element):
        pass

    class E(Element):
        a: relation_one[A]
        b: relation_many[A]
        u: relation_many[A]

    E.a = association("a", A, upper=1)
    E.b = association("b", A)
    E.u = derivedunion("u", A, 0, "*", E.a, E.b)

    e = E()
    e.a = A()
    e.b = A()

    assert e.a in e.u
    assert e.b[0] in e.u


def test_derivedunion_listmixins():
    class A(Element):
        a: relation_many[A]
        b: relation_many[A]
        u: relation_many[A]
        name: attribute[str]

    A.a = association("a", A)
    A.b = association("b", A)
    A.u = derivedunion("u", A, 0, "*", A.a, A.b)
    A.name = attribute("name", str, "default")

    a = A()
    a.a = A()
    a.a = A()
    a.b = A()
    a.a[0].name = "foo"
    a.a[1].name = "bar"
    a.b[0].name = "baz"

    assert list(a.a[:].name) == ["foo", "bar"]
    assert sorted(list(a.u[:].name)) == ["bar", "baz", "foo"]


def test_composite():
    class A(Element):
        is_unlinked = False
        name = attribute("name", str)
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
