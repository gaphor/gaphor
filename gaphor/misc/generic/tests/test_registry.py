""" Tests for :module:`gaphor.misc.generic.registry`."""

import unittest

__all__ = ("RegistryTests",)


class RegistryTests(unittest.TestCase):
    def test_one_axis_no_specificity(self):
        from gaphor.misc.generic.registry import Registry
        from gaphor.misc.generic.registry import SimpleAxis

        registry = Registry(("foo", SimpleAxis()))
        a = object()
        b = object()
        registry.register(a)
        registry.register(b, "foo")

        self.assertEqual(registry.lookup(), a)
        self.assertEqual(registry.lookup("foo"), b)
        self.assertEqual(registry.lookup("bar"), None)

    def test_two_axes(self):
        from gaphor.misc.generic.registry import Registry
        from gaphor.misc.generic.registry import SimpleAxis
        from gaphor.misc.generic.registry import TypeAxis

        registry = Registry(("type", TypeAxis()), ("name", SimpleAxis()))

        target1 = Target("one")
        registry.register(target1, object)

        target2 = Target("two")
        registry.register(target2, DummyA)

        target3 = Target("three")
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
        from gaphor.misc.generic.registry import Registry
        from gaphor.misc.generic.registry import SimpleAxis
        from gaphor.misc.generic.registry import TypeAxis

        registry = Registry(("type", TypeAxis()), ("name", SimpleAxis()))
        registry.register("one", object)
        registry.register("two", DummyA, "foo")
        self.assertEqual(registry.get_registration(object), "one")
        self.assertEqual(registry.get_registration(DummyA, "foo"), "two")
        self.assertEqual(registry.get_registration(object, "foo"), None)
        self.assertEqual(registry.get_registration(DummyA), None)

    def test_register_too_many_keys(self):
        from gaphor.misc.generic.registry import Registry
        from gaphor.misc.generic.registry import SimpleAxis

        registry = Registry(("name", SimpleAxis()))
        self.assertRaises(ValueError, registry.register, object(), "one", "two")

    def test_lookup_too_many_keys(self):
        from gaphor.misc.generic.registry import Registry
        from gaphor.misc.generic.registry import SimpleAxis

        registry = Registry(("name", SimpleAxis()))
        self.assertRaises(ValueError, registry.lookup, "one", "two")

    def test_conflict_error(self):
        from gaphor.misc.generic.registry import Registry
        from gaphor.misc.generic.registry import SimpleAxis

        registry = Registry(("name", SimpleAxis()))
        registry.register(object(), name="foo")
        self.assertRaises(ValueError, registry.register, object(), "foo")

    def test_override(self):
        from gaphor.misc.generic.registry import Registry
        from gaphor.misc.generic.registry import SimpleAxis

        registry = Registry(("name", SimpleAxis()))
        registry.register(1, name="foo")
        registry.override(2, name="foo")
        self.assertEqual(registry.lookup("foo"), 2)

    def test_skip_nodes(self):
        from gaphor.misc.generic.registry import Registry
        from gaphor.misc.generic.registry import SimpleAxis

        registry = Registry(
            ("one", SimpleAxis()), ("two", SimpleAxis()), ("three", SimpleAxis())
        )
        registry.register("foo", one=1, three=3)
        self.assertEqual(registry.lookup(1, three=3), "foo")

    def test_miss(self):
        from gaphor.misc.generic.registry import Registry
        from gaphor.misc.generic.registry import SimpleAxis

        registry = Registry(
            ("one", SimpleAxis()), ("two", SimpleAxis()), ("three", SimpleAxis())
        )
        registry.register("foo", 1, 2)
        self.assertEqual(registry.lookup(one=1, three=3), None)

    def test_bad_lookup(self):
        from gaphor.misc.generic.registry import Registry
        from gaphor.misc.generic.registry import SimpleAxis

        registry = Registry(("name", SimpleAxis()), ("grade", SimpleAxis()))
        self.assertRaises(ValueError, registry.register, 1, foo=1)
        self.assertRaises(ValueError, registry.lookup, foo=1)
        self.assertRaises(ValueError, registry.register, 1, "foo", name="foo")


class DummyA(object):
    pass


class DummyB(DummyA):
    pass


class Target(object):
    def __init__(self, name):
        self.name = name

    # Only called if being printed due to a failing test
    def __repr__(self):  # pragma NO COVERAGE
        return "Target('%s')" % self.name
