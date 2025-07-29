from __future__ import annotations

import enum

import pytest

from gaphor.core import event_handler
from gaphor.core.modeling import Base
from gaphor.core.modeling.collection import collection
from gaphor.core.modeling.event import AssociationUpdated
from gaphor.core.modeling.properties import (
    UnlimitedNatural,
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
    class A(Base):
        one: relation_one[B | None]

    class B(Base):
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
    class A(Base):
        one: relation_many[B]

    class B(Base):
        two: relation_one[A]

    A.one = association("one", B, 0, "*", opposite="two")
    B.two = association("two", A, 0, 1)

    a = A()
    b = B()
    a.one = b
    assert b in a.one
    assert b.two is a


def test_reassign_association_n_1():
    class A(Base):
        many: relation_many[B]

    class B(Base):
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
    class A(Base):
        many: relation_many[B]

    class B(Base):
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
    class A(Base):
        one: relation_one[B]

    class B(Base):
        two: relation_one[A]

    class C(Base):
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
    class A(Base):
        one: relation_one[B]

    class B(Base):
        two: relation_many[A]

    class C(Base):
        pass

    A.one = association("one", B, lower=0, upper=1, opposite="two")
    B.two = association("two", A, lower=0, upper="*", opposite="one")

    a1 = A()
    a2 = A()
    b1 = B()
    b2 = B()

    b1.two = a1
    assert len(b1.two) == 1, f"len(b1.two) == {len(b1.two)}"
    assert a1 in b1.two
    assert a1.one is b1, f"{a1.one}/{b1}"
    b1.two = a1
    b1.two = a1
    assert len(b1.two) == 1, f"len(b1.two) == {len(b1.two)}"
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

    class A(Base):
        one: relation_many[B]

    class B(Base):
        two: relation_many[A]

    class C(Base):
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
    class A(Base):
        one: relation_many[B]

    class B(Base):
        pass

    class C(Base):
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
    class A(Base):
        one: relation_many[B]

    class B(Base):
        pass

    class C(Base):
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
    class A(Base):
        one: relation_many[B]

    class B(Base):
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


def test_association_subsettable_0_n(element_factory):
    class A(Base):
        pass

    class C(Base):
        original: relation_many[A]
        subset: relation_many[A]

    C.original = association("original", A, 0, "*")
    C.subset = association("subset", A, 0, "*")

    C.original.add(C.subset)

    a1 = A()
    a2 = A()

    # Subset changes, superset has multiplicity *, subset has multiplicity 1 or *:
    #     Both sets {}: subset {a1} => superset {a1}
    c1 = C()
    assert len(c1.original) == 0
    assert len(c1.subset) == 0
    c1.subset = a1
    assert len(c1.original) == 1
    assert a1 in c1.original

    #     Superset {a1}, subset {}, subset {a2} => superset {a1, a2}
    c2 = C()
    c2.original = a1
    assert len(c2.subset) == 0
    c2.subset = a2
    assert len(c2.original) == 2
    assert a1 in c2.original
    assert a2 in c2.original

    #     Superset {a1}, subset {a1}: subset {a2}, => superset {a1, a2} ***POLICY***
    c3 = C()
    c3.subset = a1
    assert a1 in c3.original
    c3.subset.remove(a1)
    c3.subset = a2
    assert len(c3.original) == 2
    assert a2 in c3.original

    #     Superset {a1}, subset {a1}: subset {} => superset {a1} ***POLICY***
    c4 = C()
    c4.original = a1
    c4.subset = a1
    c4.subset.remove(a1)
    assert len(c4.original) == 1

    # Superset changes, superset has multiplicity *, subset has multiplicity 1 or *:
    #     Both sets {}: superset {a1} => subset {}
    c5 = C()
    c5.original = a1
    assert len(c5.subset) == 0

    #     Subset {a1}, superset {a1}: superset {} => subset {}
    c6 = C()
    c6.subset = a1
    assert len(c6.original) == 1
    c6.original.remove(a1)
    assert len(c6.subset) == 0

    #     Superset {a1}, subset {a1}, superset {a2} => subset {} ***POLICY***
    c7 = C()
    c7.subset = a1
    assert a1 in c7.original
    c7.original.remove(a1)
    c7.original = a2
    assert len(c7.subset) == 0


def test_association_subsettable_0_1(element_factory):
    class A(Base):
        pass

    class C(Base):
        original: relation_many[A]
        subset: relation_many[A]

    C.original = association("original", A, 0, 1)
    C.subset = association("subset", A, 0, 1)

    C.original.add(C.subset)

    a1 = A()
    a2 = A()

    # Subset changes, superset has multiplicity 0..1, subset has multiplicity 0..1:
    #     Both sets {}: subset {a1} => superset {a1}
    c1 = C()
    assert c1.original is None
    assert c1.subset is None
    c1.subset = a1
    assert c1.original is a1

    #     Superset {a1}, subset {}, subset {a2} => superset {a2}
    c2 = C()
    c2.original = a1
    assert c2.subset is None
    c2.subset = a2
    assert c2.original is a2

    #     Superset {a1}, subset {a1}: subset {a2}, => superset {a2} ***POLICY***
    c3 = C()
    c3.subset = a1
    assert c3.original is a1
    c3.subset = a2
    assert c3.original is a2

    #     Superset {a1}, subset {a1}: subset {} => superset {} ***POLICY***
    c4 = C()
    c4.original = a1
    c4.subset = a1
    c4.subset = None
    assert c4.original is None

    # Superset changes, superset has multiplicity *, subset has multiplicity 1 or *:
    #     Both sets {}: superset {a1} => subset {}
    c5 = C()
    c5.original = a1
    assert c5.subset is None

    #     Subset {a1}, superset {a1}: superset {} => subset {}
    c6 = C()
    c6.subset = a1
    assert c6.original is a1
    c6.original = None
    assert c6.subset is None

    #     Superset {a1}, subset {a1}, superset {a2} => subset {} ***POLICY***
    c7 = C()
    c7.subset = a1
    assert c7.original is a1
    c7.original = a2
    assert c7.subset is None


def test_association_subsettable_updates_derived_union(element_factory):
    class A(Base):
        pass

    class C(Base):
        original: relation_many[A]
        subset: relation_many[A]
        union: relation_many[A]

    C.original = association("original", A, 0, 1)
    C.subset = association("subset", A, 0, 1)
    C.original.add(C.subset)
    C.union = derivedunion("u", object, 0, "*", C.original)

    a1 = A()
    a2 = A()

    c1 = C()
    c1.subset = a1
    assert a1 in c1.union
    c1.subset = a2
    assert a2 in c1.union
    assert a1 not in c1.union


# def test_association_subsettable_add_fails_when_subset_multiplicity_exceeds_superset_multiplicity(element_factory):
#     class A(Base):
#         pass

#     class C(Base):
#         original: relation_many[A]
#         subset: relation_many[A]

#     C.original = association("original", A, 0, 1)
#     C.subset = association("subset", A, 0, "*")

#     with pytest.raises(Exception) as execinfo:
#         C.original.add(C.subset)
#     # assert str(execinfo.value) == "Cannot add a multiplicity * subset to a multiplicity 1 superset"


def test_can_not_set_association_to_owner(element_factory, event_manager):
    class A(Base):
        pass

    A.a = association("a", A, upper=1)

    a = element_factory.create(A)

    with pytest.raises(TypeError):
        a.a = a


def test_attributes():
    class A(Base):
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


@pytest.mark.parametrize(
    "input,expected",
    [
        [None, None],
        [0, 0],
        [1, 1],
        [2, 2],
        [False, 0],
        [True, 1],
        ["False", 0],
        ["True", 1],
    ],
)
def test_int_and_boolean_attributes(input, expected):
    class A(Base):
        a = attribute("a", int, 0)

    a = A()
    a.a = input

    assert a.a == expected


@pytest.mark.parametrize(
    "input,expected",
    [
        [None, None],
        [0, 0],
        [1, 1],
        [2, 2],
        ["*", "*"],
    ],
)
def test_unlimited_natural_attributes(input, expected):
    class A(Base):
        a = attribute("a", UnlimitedNatural, 0)

    a = A()
    a.a = input

    assert a.a == expected


@pytest.mark.parametrize(
    "input",
    [
        "foo",
        -1,
    ],
)
def test_unlimited_natural_attributes_wrong_inputs(input):
    class A(Base):
        a = attribute("a", UnlimitedNatural, 0)

    a = A()

    with pytest.raises(ValueError):
        a.a = input


def test_attributes_loading_failure():
    class A(Base):
        a: attribute[int]

    A.a = attribute("a", int, 0)

    a = A()

    with pytest.raises(ValueError):
        A.a.load(a, "not-int")


def test_enumerations():
    class EnumKind(enum.StrEnum):
        one = "one"
        two = "two"
        three = "three"

    class A(Base):
        a: enumeration

    A.a = enumeration("a", EnumKind, EnumKind.one)
    a = A()
    assert a.a == "one"
    a.a = "two"
    assert a.a == "two"
    a.a = "three"
    assert a.a == "three"

    with pytest.raises(TypeError):
        a.a = "four"

    assert a.a == EnumKind.three

    del a.a
    assert a.a == "one"


def test_derived():
    class A(Base):
        a: relation_many[A]

    A.a = derived("a", str, 0, "*", lambda self: ["a", "b", "c"])

    a = A()

    assert isinstance(a.a, collection)
    assert a.a == ["a", "b", "c"]


def test_derived_single_properties():
    class A(Base):
        pass

    class E(Base):
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
    class A(Base):
        pass

    class E(Base):
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
    class A(Base):
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
    class A(Base):
        pass

    class E(Base):
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
    class A(Base):
        pass

    class E(Base):
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
    class A(Base):
        pass

    class E(Base):
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
    class A(Base):
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
    assert sorted(a.u[:].name) == ["bar", "baz", "foo"]


def test_composite():
    class A(Base):
        is_unlinked = False
        name = attribute("name", str)
        comp: relation_many[A]
        other: relation_many[A]

        def unlink(self):
            self.is_unlinked = True
            Base.unlink(self)

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
