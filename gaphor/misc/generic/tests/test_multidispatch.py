""" Tests for :module:`gaphor.misc.generic.multidispatch`."""

import unittest

__all__ = ("DispatcherTests",)


class DispatcherTests(unittest.TestCase):
    def createDispatcher(
        self, params_arity, args=None, varargs=None, keywords=None, defaults=None
    ):
        from inspect import ArgSpec
        from gaphor.misc.generic.multidispatch import FunctionDispatcher

        return FunctionDispatcher(
            ArgSpec(args=args, varargs=varargs, keywords=keywords, defaults=defaults),
            params_arity,
        )

    def test_one_argument(self):
        dispatcher = self.createDispatcher(1, args=["x"])

        dispatcher.register_rule(lambda x: x + 1, int)
        self.assertEqual(dispatcher(1), 2)
        self.assertRaises(TypeError, dispatcher, "s")

        dispatcher.register_rule(lambda x: x + "1", str)
        self.assertEqual(dispatcher(1), 2)
        self.assertEqual(dispatcher("1"), "11")
        self.assertRaises(TypeError, dispatcher, tuple())

    def test_two_arguments(self):
        dispatcher = self.createDispatcher(2, args=["x", "y"])

        dispatcher.register_rule(lambda x, y: x + y + 1, int, int)
        self.assertEqual(dispatcher(1, 2), 4)
        self.assertRaises(TypeError, dispatcher, "s", "ss")
        self.assertRaises(TypeError, dispatcher, 1, "ss")
        self.assertRaises(TypeError, dispatcher, "s", 2)

        dispatcher.register_rule(lambda x, y: x + y + "1", str, str)
        self.assertEqual(dispatcher(1, 2), 4)
        self.assertEqual(dispatcher("1", "2"), "121")
        self.assertRaises(TypeError, dispatcher, "1", 1)
        self.assertRaises(TypeError, dispatcher, 1, "1")

        dispatcher.register_rule(lambda x, y: str(x) + y + "1", int, str)
        self.assertEqual(dispatcher(1, 2), 4)
        self.assertEqual(dispatcher("1", "2"), "121")
        self.assertEqual(dispatcher(1, "2"), "121")
        self.assertRaises(TypeError, dispatcher, "1", 1)

    def test_bottom_rule(self):
        dispatcher = self.createDispatcher(1, args=["x"])

        dispatcher.register_rule(lambda x: x, object)
        self.assertEqual(dispatcher(1), 1)
        self.assertEqual(dispatcher("1"), "1")
        self.assertEqual(dispatcher([1]), [1])
        self.assertEqual(dispatcher((1,)), (1,))

    def test_subtype_evaluation(self):
        class Super(object):
            pass

        class Sub(Super):
            pass

        dispatcher = self.createDispatcher(1, args=["x"])

        dispatcher.register_rule(lambda x: x, Super)
        o_super = Super()
        self.assertEqual(dispatcher(o_super), o_super)
        o_sub = Sub()
        self.assertEqual(dispatcher(o_sub), o_sub)
        self.assertRaises(TypeError, dispatcher, object())

        dispatcher.register_rule(lambda x: (x, x), Sub)
        o_super = Super()
        self.assertEqual(dispatcher(o_super), o_super)
        o_sub = Sub()
        self.assertEqual(dispatcher(o_sub), (o_sub, o_sub))

    def test_register_rule_with_wrong_arity(self):
        dispatcher = self.createDispatcher(1, args=["x"])
        dispatcher.register_rule(lambda x: x, int)
        self.assertRaises(TypeError, dispatcher.register_rule, lambda x, y: x, str)

    def test_register_rule_with_different_arg_names(self):
        dispatcher = self.createDispatcher(1, args=["x"])
        dispatcher.register_rule(lambda y: y, int)
        self.assertEqual(dispatcher(1), 1)

    def test_dispatching_with_varargs(self):
        dispatcher = self.createDispatcher(1, args=["x"], varargs="va")
        dispatcher.register_rule(lambda x, *va: x, int)
        self.assertEqual(dispatcher(1), 1)
        self.assertRaises(TypeError, dispatcher, "1", 2, 3)

    def test_dispatching_with_varkw(self):
        dispatcher = self.createDispatcher(1, args=["x"], keywords="vk")
        dispatcher.register_rule(lambda x, **vk: x, int)
        self.assertEqual(dispatcher(1), 1)
        self.assertRaises(TypeError, dispatcher, "1", a=1, b=2)

    def test_dispatching_with_kw(self):
        dispatcher = self.createDispatcher(1, args=["x", "y"], defaults=["vk"])
        dispatcher.register_rule(lambda x, y=1: x, int)
        self.assertEqual(dispatcher(1), 1)
        self.assertRaises(TypeError, dispatcher, "1", k=1)

    def test_create_dispatcher_with_pos_args_less_multi_arity(self):
        self.assertRaises(TypeError, self.createDispatcher, 2, args=["x"])
        self.assertRaises(
            TypeError, self.createDispatcher, 2, args=["x", "y"], defaults=["x"]
        )

    def test_register_rule_with_wrong_number_types_parameters(self):
        dispatcher = self.createDispatcher(1, args=["x", "y"])
        self.assertRaises(TypeError, dispatcher.register_rule, lambda x, y: x, int, str)

    def test_register_rule_with_partial_dispatching(self):
        dispatcher = self.createDispatcher(1, args=["x", "y"])
        dispatcher.register_rule(lambda x, y: x, int)
        self.assertEqual(dispatcher(1, 2), 1)
        self.assertEqual(dispatcher(1, "2"), 1)
        self.assertRaises(TypeError, dispatcher, "2", 1)
        dispatcher.register_rule(lambda x, y: x, str)
        self.assertEqual(dispatcher(1, 2), 1)
        self.assertEqual(dispatcher(1, "2"), 1)
        self.assertEqual(dispatcher("1", "2"), "1")
        self.assertEqual(dispatcher("1", 2), "1")


class MultifunctionTests(unittest.TestCase):
    def test_it(self):
        from gaphor.misc.generic.multidispatch import multifunction

        @multifunction(int, str)
        def func(x, y):
            return str(x) + y

        self.assertEqual(func(1, "2"), "12")
        self.assertRaises(TypeError, func, 1, 2)
        self.assertRaises(TypeError, func, "1", 2)
        self.assertRaises(TypeError, func, "1", "2")

        @func.when(str, str)
        def func(x, y):
            return x + y

        self.assertEqual(func(1, "2"), "12")
        self.assertEqual(func("1", "2"), "12")
        self.assertRaises(TypeError, func, 1, 2)
        self.assertRaises(TypeError, func, "1", 2)

    def test_overriding(self):
        from gaphor.misc.generic.multidispatch import multifunction

        @multifunction(int, str)
        def func(x, y):
            return str(x) + y

        self.assertEqual(func(1, "2"), "12")
        self.assertRaises(ValueError, func.when(int, str), lambda x, y: str(x))

        @func.override(int, str)
        def func(x, y):
            return y + str(x)

        self.assertEqual(func(1, "2"), "21")


class MultimethodTests(unittest.TestCase):
    def test_multimethod(self):
        from gaphor.misc.generic.multidispatch import multimethod
        from gaphor.misc.generic.multidispatch import has_multimethods

        @has_multimethods
        class Dummy(object):
            @multimethod(int)
            def foo(self, x):
                return x + 1

            @foo.when(str)
            def foo(self, x):
                return x + "1"

        self.assertEqual(Dummy().foo(1), 2)
        self.assertEqual(Dummy().foo("1"), "11")
        self.assertRaises(TypeError, Dummy().foo, [])

    def test_inheritance(self):
        from gaphor.misc.generic.multidispatch import multimethod
        from gaphor.misc.generic.multidispatch import has_multimethods

        @has_multimethods
        class Dummy(object):
            @multimethod(int)
            def foo(self, x):
                return x + 1

            @foo.when(float)
            def foo(self, x):
                return x + 1.5

        @has_multimethods
        class DummySub(Dummy):
            @Dummy.foo.when(str)
            def foo(self, x):
                return x + "1"

            @foo.when(tuple)
            def foo(self, x):
                return x + (1,)

            @Dummy.foo.when(bool)
            def foo(self, x):
                return not x

        self.assertEqual(Dummy().foo(1), 2)
        self.assertEqual(Dummy().foo(1.5), 3.0)
        self.assertRaises(TypeError, Dummy().foo, "1")
        self.assertEqual(DummySub().foo(1), 2)
        self.assertEqual(DummySub().foo(1.5), 3.0)
        self.assertEqual(DummySub().foo("1"), "11")
        self.assertEqual(DummySub().foo((1, 2)), (1, 2, 1))
        self.assertEqual(DummySub().foo(True), False)
        self.assertRaises(TypeError, DummySub().foo, [])

    def test_override(self):
        from gaphor.misc.generic.multidispatch import multimethod
        from gaphor.misc.generic.multidispatch import has_multimethods

        @has_multimethods
        class Dummy(object):
            @multimethod(str, str)
            def foo(self, x, y):
                return x + y

            @foo.when(str, str)
            def foo(self, x, y):
                return y + x

        self.assertEqual(Dummy().foo("1", "2"), "21")

    def test_inheritance_override(self):
        from gaphor.misc.generic.multidispatch import multimethod
        from gaphor.misc.generic.multidispatch import has_multimethods

        @has_multimethods
        class Dummy(object):
            @multimethod(int)
            def foo(self, x):
                return x + 1

        @has_multimethods
        class DummySub(Dummy):
            @Dummy.foo.when(int)
            def foo(self, x):
                return x + 2

        self.assertEqual(Dummy().foo(1), 2)
        self.assertEqual(DummySub().foo(1), 3)
