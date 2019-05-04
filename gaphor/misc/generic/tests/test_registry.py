""" Tests for :module:`gaphor.misc.generic.registry`."""

import unittest

from gaphor.misc.generic.registry import Registry, SimpleAxis, TypeAxis

__all__ = ("RegistryTests",)


class DummyA(object):
    pass


class DummyB(DummyA):
    pass


class RegistryTests(unittest.TestCase):
    def test_one_axis_no_specificity(self):
        registry = Registry(("foo", SimpleAxis()))
        a = object()
        b = object()
        registry.register(a)
        registry.register(b, "foo")

        self.assertEqual(registry.lookup(), a)
        self.assertEqual(registry.lookup("foo"), b)
        self.assertEqual(registry.lookup("bar"), None)

    def test_subtyping_on_axes(self):
        registry = Registry(("type", TypeAxis()))

        target1 = "one"
        registry.register(target1, object)

        target2 = "two"
        registry.register(target2, DummyA)

        target3 = "three"
        registry.register(target3, DummyB)

        self.assertEqual(registry.lookup(object()), target1)
        self.assertEqual(registry.lookup(DummyA()), target2)
        self.assertEqual(registry.lookup(DummyB()), target3)

    def test_query_subtyping_on_axes(self):
        registry = Registry(("type", TypeAxis()))

        target1 = "one"
        registry.register(target1, object)

        target2 = "two"
        registry.register(target2, DummyA)

        target3 = "three"
        registry.register(target3, DummyB)

        target4 = "four"
        registry.register(target4, int)

        self.assertEqual(list(registry.query(object())), [target1])
        self.assertEqual(list(registry.query(DummyA())), [target2, target1])
        self.assertEqual(list(registry.query(DummyB())), [target3, target2, target1])
        self.assertEqual(list(registry.query(3)), [target4, target1])

    def test_two_axes(self):
        registry = Registry(("type", TypeAxis()), ("name", SimpleAxis()))

        target1 = "one"
        registry.register(target1, object)

        target2 = "two"
        registry.register(target2, DummyA)

        target3 = "three"
        registry.register(target3, DummyA, "foo")

        context1 = object()
        self.assertEqual(registry.lookup(context1), target1)

        context2 = DummyB()
        self.assertEqual(registry.lookup(context2), target2)
        self.assertEqual(registry.lookup(context2, "foo"), target3)

        target4 = object()
        registry.register(target4, DummyB)

        self.assertEqual(registry.lookup(context2), target4)
        self.assertEqual(registry.lookup(context2, "foo"), target3)

    def test_get_registration(self):
        registry = Registry(("type", TypeAxis()), ("name", SimpleAxis()))
        registry.register("one", object)
        registry.register("two", DummyA, "foo")
        self.assertEqual(registry.get_registration(object), "one")
        self.assertEqual(registry.get_registration(DummyA, "foo"), "two")
        self.assertEqual(registry.get_registration(object, "foo"), None)
        self.assertEqual(registry.get_registration(DummyA), None)

    def test_register_too_many_keys(self):
        registry = Registry(("name", SimpleAxis()))
        self.assertRaises(ValueError, registry.register, object(), "one", "two")

    def test_lookup_too_many_keys(self):
        registry = Registry(("name", SimpleAxis()))
        self.assertRaises(ValueError, registry.lookup, "one", "two")

    def test_conflict_error(self):
        registry = Registry(("name", SimpleAxis()))
        registry.register(object(), name="foo")
        self.assertRaises(ValueError, registry.register, object(), "foo")

    def test_skip_nodes(self):
        registry = Registry(
            ("one", SimpleAxis()), ("two", SimpleAxis()), ("three", SimpleAxis())
        )
        registry.register("foo", one=1, three=3)
        self.assertEqual(registry.lookup(1, three=3), "foo")

    def test_miss(self):
        registry = Registry(
            ("one", SimpleAxis()), ("two", SimpleAxis()), ("three", SimpleAxis())
        )
        registry.register("foo", 1, 2)
        self.assertEqual(registry.lookup(one=1, three=3), None)

    def test_bad_lookup(self):
        registry = Registry(("name", SimpleAxis()), ("grade", SimpleAxis()))
        self.assertRaises(ValueError, registry.register, 1, foo=1)
        self.assertRaises(ValueError, registry.lookup, foo=1)
        self.assertRaises(ValueError, registry.register, 1, "foo", name="foo")
