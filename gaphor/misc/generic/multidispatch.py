""" Multidispatch for functions and methods.

This code is a Python 3, slimmed down version of the
generic package by Andrey Popp.

Only the generic function code is left in tact -- no generic methods.
The interface has been made in line with `functools.singledispatch`.

Note that this module does not support annotated functions.
"""

from typing import cast, Any, Callable, Tuple, Type

import functools
import inspect

from gaphor.misc.generic.registry import Registry, TypeAxis

__all__ = "multidispatch"


def multidispatch(
    *argtypes: Type[object]
) -> Callable[[Callable[..., Any]], "FunctionDispatcher"]:
    """ Declare function as multidispatch

    This decorator takes ``argtypes`` argument types and replace decorated
    function with :class:`.FunctionDispatcher` object, which is responsible for
    multiple dispatch feature.
    """

    def _replace_with_dispatcher(func: Callable[..., Any]) -> "FunctionDispatcher":
        nonlocal argtypes
        argspec = inspect.getfullargspec(func)
        if not argtypes:
            arity = _arity(argspec)
            if isinstance(func, type):
                # It's a class we deal with:
                arity -= 1
            argtypes = (object,) * arity

        dispatcher = functools.update_wrapper(
            FunctionDispatcher(argspec, len(argtypes)), func
        )
        dispatcher.register_rule(func, *argtypes)
        return dispatcher

    return _replace_with_dispatcher


class FunctionDispatcher:
    """ Multidispatcher for functions

    This object dispatch calls to function by its argument types. Usually it is
    produced by :func:`.multidispatch` decorator.

    You should not manually create objects of this type.
    """

    def __init__(self, argspec: "inspect.FullArgSpec", params_arity: int):
        """ Initialize dispatcher with ``argspec`` of type
        :class:`inspect.ArgSpec` and ``params_arity`` that represent number
        params."""
        # Check if we have enough positional arguments for number of type params
        if _arity(argspec) < params_arity:
            raise TypeError(
                "Not enough positional arguments "
                "for number of type parameters provided."
            )

        self.argspec = argspec
        self.params_arity = params_arity

        axis = [(f"arg_{n:d}", TypeAxis()) for n in range(params_arity)]
        self.registry = Registry[type, Callable[..., Any]](*axis)

    def check_rule(self, rule: Callable[..., Any], *argtypes: Any) -> None:
        # Check if we have the right number of parametrized types
        if len(argtypes) != self.params_arity:
            raise TypeError(
                f"Wrong number of type parameters: have {len(argtypes)}, expected {self.params_arity}."
            )

        # Check if we have the same argspec (by number of args)
        rule_argspec = inspect.getfullargspec(rule)  # type ignore
        left_spec = tuple(x and len(x) or 0 for x in rule_argspec[:4])
        right_spec = tuple(x and len(x) or 0 for x in self.argspec[:4])
        if left_spec != right_spec:
            raise TypeError("Rule does not conform to previous implementations.")

    def register_rule(self, rule: Callable[..., Any], *argtypes: Any) -> None:
        """ Register new ``rule`` for ``argtypes``."""
        self.check_rule(rule, *argtypes)
        self.registry.register(rule, *argtypes)

    def register(self, *argtypes: Any) -> Callable[..., Any]:
        """ Decorator for registering new case for multidispatch

        New case will be registered for types identified by ``argtypes``. The
        length of ``argtypes`` should be equal to the length of ``argtypes``
        argument were passed corresponding :func:`.multidispatch` call, which
        also indicated the number of arguments multidispatch dispatches on.
        """

        def register_rule(func: Callable[..., Any]) -> Callable[..., Any]:
            self.register_rule(func, *argtypes)
            return func

        return register_rule

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        """ Dispatch call to appropriate rule."""
        trimmed_args = args[: self.params_arity]
        rule = self.registry.lookup(*trimmed_args)
        if not rule:
            raise TypeError(f"No available rule found for {trimmed_args!r}")
        return rule(*args, **kwargs)


def _arity(argspec: "inspect.FullArgSpec") -> int:
    """ Determinal positional arity of argspec."""
    args = argspec.args if argspec.args else []
    defaults = argspec.defaults if argspec.defaults else []
    return len(args) - len(defaults)
