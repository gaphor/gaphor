""" Tests for :module:`gaphor.misc.generic.registry`."""

import pytest

from typing import Union
from gaphor.misc.generic.registry import Registry, SimpleAxis, TypeAxis


class DummyA:
    pass


class DummyB(DummyA):
    pass


def test_one_axis_no_specificity():
    registry: Registry[object] = Registry(("foo", SimpleAxis()))
    a = object()
    b = object()
    registry.register(a)
    registry.register(b, "foo")

    assert registry.lookup() == a
    assert registry.lookup("foo") == b
    assert registry.lookup("bar") is None


def test_subtyping_on_axes():
    registry: Registry[str] = Registry(("type", TypeAxis()))

    target1 = "one"
    registry.register(target1, object)

    target2 = "two"
    registry.register(target2, DummyA)

    target3 = "three"
    registry.register(target3, DummyB)

    assert registry.lookup(object()) == target1
    assert registry.lookup(DummyA()) == target2
    assert registry.lookup(DummyB()) == target3


def test_query_subtyping_on_axes():
    registry: Registry[str] = Registry(("type", TypeAxis()))

    target1 = "one"
    registry.register(target1, object)

    target2 = "two"
    registry.register(target2, DummyA)

    target3 = "three"
    registry.register(target3, DummyB)

    target4 = "four"
    registry.register(target4, int)

    assert list(registry.query(object())) == [target1]
    assert list(registry.query(DummyA())) == [target2, target1]
    assert list(registry.query(DummyB())) == [target3, target2, target1]
    assert list(registry.query(3)) == [target4, target1]


def test_two_axes():
    registry: Registry[Union[str, object]] = Registry(
        ("type", TypeAxis()), ("name", SimpleAxis())
    )

    target1 = "one"
    registry.register(target1, object)

    target2 = "two"
    registry.register(target2, DummyA)

    target3 = "three"
    registry.register(target3, DummyA, "foo")

    context1 = object()
    assert registry.lookup(context1) == target1

    context2 = DummyB()
    assert registry.lookup(context2) == target2
    assert registry.lookup(context2, "foo") == target3

    target4 = object()
    registry.register(target4, DummyB)

    assert registry.lookup(context2) == target4
    assert registry.lookup(context2, "foo") == target3


def test_get_registration():
    registry: Registry[str] = Registry(("type", TypeAxis()), ("name", SimpleAxis()))
    registry.register("one", object)
    registry.register("two", DummyA, "foo")
    assert registry.get_registration(object) == "one"
    assert registry.get_registration(DummyA, "foo") == "two"
    assert registry.get_registration(object, "foo") is None
    assert registry.get_registration(DummyA) is None


def test_register_too_many_keys():
    registry: Registry[type] = Registry(("name", SimpleAxis()))
    with pytest.raises(ValueError):
        registry.register(object, "one", "two")


def test_lookup_too_many_keys():
    registry: Registry[object] = Registry(("name", SimpleAxis()))
    with pytest.raises(ValueError):
        registry.register(registry.lookup("one", "two"))


def test_conflict_error():
    registry: Registry[Union[object, type]] = Registry(("name", SimpleAxis()))
    registry.register(object(), name="foo")
    with pytest.raises(ValueError):
        registry.register(object, "foo")


def test_skip_nodes():
    registry: Registry[str] = Registry(
        ("one", SimpleAxis()), ("two", SimpleAxis()), ("three", SimpleAxis())
    )
    registry.register("foo", one=1, three=3)
    assert registry.lookup(1, three=3) == "foo"


def test_miss():
    registry: Registry[str] = Registry(
        ("one", SimpleAxis()), ("two", SimpleAxis()), ("three", SimpleAxis())
    )
    registry.register("foo", 1, 2)
    assert registry.lookup(one=1, three=3) is None


def test_bad_lookup():
    registry: Registry[int] = Registry(("name", SimpleAxis()), ("grade", SimpleAxis()))
    with pytest.raises(ValueError):
        registry.register(1, foo=1)
    with pytest.raises(ValueError):
        registry.lookup(foo=1)
    with pytest.raises(ValueError):
        registry.register(1, "foo", name="foo")
