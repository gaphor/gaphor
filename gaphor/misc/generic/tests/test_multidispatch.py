""" Tests for :module:`gaphor.misc.generic.multidispatch`."""

import pytest

from gaphor.misc.generic.multidispatch import multidispatch


def create_dispatcher(
    params_arity, args=None, varargs=None, keywords=None, defaults=None
):
    from inspect import ArgSpec
    from gaphor.misc.generic.multidispatch import FunctionDispatcher

    return FunctionDispatcher(
        ArgSpec(args=args, varargs=varargs, keywords=keywords, defaults=defaults),
        params_arity,
    )


def test_one_argument():
    dispatcher = create_dispatcher(1, args=["x"])

    dispatcher.register_rule(lambda x: x + 1, int)
    assert dispatcher(1) == 2
    with pytest.raises(TypeError):
        dispatcher("s")

    dispatcher.register_rule(lambda x: x + "1", str)
    assert dispatcher(1) == 2
    assert dispatcher("1") == "11"
    with pytest.raises(TypeError):
        dispatcher(tuple())


def test_two_arguments():
    dispatcher = create_dispatcher(2, args=["x", "y"])

    dispatcher.register_rule(lambda x, y: x + y + 1, int, int)
    assert dispatcher(1, 2) == 4
    with pytest.raises(TypeError):
        dispatcher("s", "ss")
    with pytest.raises(TypeError):
        dispatcher(1, "ss")
    with pytest.raises(TypeError):
        dispatcher("s", 2)

    dispatcher.register_rule(lambda x, y: x + y + "1", str, str)
    assert dispatcher(1, 2) == 4
    assert dispatcher("1", "2") == "121"
    with pytest.raises(TypeError):
        dispatcher("1", 1)
    with pytest.raises(TypeError):
        dispatcher(1, "1")

    dispatcher.register_rule(lambda x, y: str(x) + y + "1", int, str)
    assert dispatcher(1, 2) == 4
    assert dispatcher("1", "2") == "121"
    assert dispatcher(1, "2") == "121"
    with pytest.raises(TypeError):
        dispatcher("1", 1)


def test_bottom_rule():
    dispatcher = create_dispatcher(1, args=["x"])

    dispatcher.register_rule(lambda x: x, object)
    assert dispatcher(1) == 1
    assert dispatcher("1") == "1"
    assert dispatcher([1]) == [1]
    assert dispatcher((1,)) == (1,)


def test_subtype_evaluation():
    class Super:
        pass

    class Sub(Super):
        pass

    dispatcher = create_dispatcher(1, args=["x"])

    dispatcher.register_rule(lambda x: x, Super)
    o_super = Super()
    assert dispatcher(o_super) == o_super
    o_sub = Sub()
    assert dispatcher(o_sub) == o_sub
    with pytest.raises(TypeError):
        dispatcher(object())

    dispatcher.register_rule(lambda x: (x, x), Sub)
    o_super = Super()
    assert dispatcher(o_super) == o_super
    o_sub = Sub()
    assert dispatcher(o_sub) == (o_sub, o_sub)


def test_register_rule_with_wrong_arity():
    dispatcher = create_dispatcher(1, args=["x"])
    dispatcher.register_rule(lambda x: x, int)
    with pytest.raises(TypeError):
        dispatcher.register_rule(lambda x, y: x, str)


def test_register_rule_with_different_arg_names():
    dispatcher = create_dispatcher(1, args=["x"])
    dispatcher.register_rule(lambda y: y, int)
    assert dispatcher(1) == 1


def test_dispatching_with_varargs():
    dispatcher = create_dispatcher(1, args=["x"], varargs="va")
    dispatcher.register_rule(lambda x, *va: x, int)
    assert dispatcher(1) == 1
    with pytest.raises(TypeError):
        dispatcher("1", 2, 3)


def test_dispatching_with_varkw():
    dispatcher = create_dispatcher(1, args=["x"], keywords="vk")
    dispatcher.register_rule(lambda x, **vk: x, int)
    assert dispatcher(1) == 1
    with pytest.raises(TypeError):
        dispatcher("1", a=1, b=2)


def test_dispatching_with_kw():
    dispatcher = create_dispatcher(1, args=["x", "y"], defaults=["vk"])
    dispatcher.register_rule(lambda x, y=1: x, int)
    assert dispatcher(1) == 1
    with pytest.raises(TypeError):
        dispatcher("1", k=1)


def test_create_dispatcher_with_pos_args_less_multi_arity():
    with pytest.raises(TypeError):
        create_dispatcher(2, args=["x"])
    with pytest.raises(TypeError):
        create_dispatcher(2, args=["x", "y"], defaults=["x"])


def test_register_rule_with_wrong_number_types_parameters():
    dispatcher = create_dispatcher(1, args=["x", "y"])
    with pytest.raises(TypeError):
        dispatcher.register_rule(lambda x, y: x, int, str)


def test_register_rule_with_partial_dispatching():
    dispatcher = create_dispatcher(1, args=["x", "y"])
    dispatcher.register_rule(lambda x, y: x, int)
    assert dispatcher(1, 2) == 1
    assert dispatcher(1, "2") == 1
    with pytest.raises(TypeError):
        dispatcher("2", 1)
    dispatcher.register_rule(lambda x, y: x, str)
    assert dispatcher(1, 2) == 1
    assert dispatcher(1, "2") == 1
    assert dispatcher("1", "2") == "1"
    assert dispatcher("1", 2) == "1"


def test_default_dispatcher():
    @multidispatch(int, str)
    def func(x, y):
        return str(x) + y

    assert func(1, "2") == "12"
    with pytest.raises(TypeError):
        func(1, 2)
    with pytest.raises(TypeError):
        func("1", 2)
    with pytest.raises(TypeError):
        func("1", "2")


def test_multiple_functions():
    @multidispatch(int, str)
    def func(x, y):
        return str(x) + y

    @func.register(str, str)
    def _(x, y):
        return x + y

    assert func(1, "2") == "12"
    assert func("1", "2") == "12"
    with pytest.raises(TypeError):
        func(1, 2)
    with pytest.raises(TypeError):
        func("1", 2)


def test_default():
    @multidispatch()
    def func(x, y):
        return x + y

    @func.register(str, str)
    def _(x, y):
        return y + x

    assert func(1, 1) == 2
    assert func("1", "2") == "21"


def test_on_classes():
    @multidispatch()
    class A:
        def __init__(self, a, b):
            self.v = a + b

    @A.register(str, str)
    class B:
        def __init__(self, a, b):
            self.v = b + a

    assert A(1, 1).v == 2
    assert A("1", "2").v == "21"
