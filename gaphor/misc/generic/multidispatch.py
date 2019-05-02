""" Multidispatch for functions and methods"""

import functools
import inspect
import types
import threading

from .registry import Registry, TypeAxis

__all__ = ("multifunction", "multimethod", "has_multimethods")


def multifunction(*argtypes):
    """ Declare function as multifunction

    This decorator takes ``argtypes`` argument types and replace decorated
    function with :class:`.FunctionDispatcher` object, which is responsible for
    multiple dispatch feature.
    """

    def _replace_with_dispatcher(func):
        dispatcher = _make_dispatcher(FunctionDispatcher, func, len(argtypes))
        dispatcher.register_rule(func, *argtypes)
        return dispatcher

    return _replace_with_dispatcher


def multimethod(*argtypes):
    """ Declare method as multimethod

    This decorator works exactly the same as :func:`.multifunction` decorator
    but replaces decorated method with :class:`.MethodDispatcher` object
    instead.

    Should be used only for decorating methods and enclosing class should have
    :func:`.has_multimethods` decorator.
    """

    def _replace_with_dispatcher(func):
        dispatcher = _make_dispatcher(MethodDispatcher, func, len(argtypes) + 1)
        dispatcher.register_unbound_rule(func, *argtypes)
        return dispatcher

    return _replace_with_dispatcher


def has_multimethods(cls):
    """ Declare class as one that have multimethods

    Should only be used for decorating classes which have methods decorated with
    :func:`.multimethod` decorator.
    """
    for name, obj in cls.__dict__.items():
        if isinstance(obj, MethodDispatcher):
            obj.proceed_unbound_rules(cls)
    return cls


class FunctionDispatcher(object):
    """ Multidispatcher for functions

    This object dispatch calls to function by its argument types. Usually it is
    produced by :func:`.multifunction` decorator.

    You should not manually create objects of this type.
    """

    def __init__(self, argspec, params_arity):
        """ Initialize dispatcher with ``argspec`` of type
        :class:`inspect.ArgSpec` and ``params_arity`` that represent number
        params."""
        # Check if we have enough positional arguments for number of type params
        if arity(argspec) < params_arity:
            raise TypeError(
                "Not enough positional arguments "
                "for number of type parameters provided."
            )

        self.argspec = argspec
        self.params_arity = params_arity

        axis = [("arg_%d" % n, TypeAxis()) for n in range(params_arity)]
        self.registry = Registry(*axis)

    def check_rule(self, rule, *argtypes):
        # Check if we have the right number of parametrized types
        if len(argtypes) != self.params_arity:
            raise TypeError("Wrong number of type parameters.")

        # Check if we have the same argspec (by number of args)
        rule_argspec = inspect.getfullargspec(rule)
        if not is_equalent_argspecs(rule_argspec, self.argspec):
            raise TypeError("Rule does not conform " "to previous implementations.")

    def register_rule(self, rule, *argtypes):
        """ Register new ``rule`` for ``argtypes``."""
        self.check_rule(rule, *argtypes)
        self.registry.register(rule, *argtypes)

    def override_rule(self, rule, *argtypes):
        """ Override ``rule`` for ``argtypes``."""
        self.check_rule(rule, *argtypes)
        self.registry.override(rule, *argtypes)

    def lookup_rule(self, *args):
        """ Lookup rule by ``args``. Returns None if no rule was found."""
        args = args[: self.params_arity]
        rule = self.registry.lookup(*args)
        if rule is None:
            raise TypeError("No available rule found for %r" % (args,))
        return rule

    def when(self, *argtypes):
        """ Decorator for registering new case for multifunction

        New case will be registered for types identified by ``argtypes``. The
        length of ``argtypes`` should be equal to the length of ``argtypes``
        argument were passed corresponding :func:`.multifunction` call, which
        also indicated the number of arguments multifunction dispatches on.
        """

        def register_rule(func):
            self.register_rule(func, *argtypes)
            return self

        return register_rule

    @property
    def otherwise(self):
        """ Decorator which registeres "catch-all" case for multifunction"""

        def register_rule(func):
            self.register_rule(func, [object] * self.params_arity)
            return self

        return register_rule

    def override(self, *argtypes):
        """ Decorator for overriding case for ``argtypes``"""

        def override_rule(func):
            self.override_rule(func, *argtypes)
            return self

        return override_rule

    def __call__(self, *args, **kwargs):
        """ Dispatch call to appropriate rule."""
        rule = self.lookup_rule(*args)
        return rule(*args, **kwargs)


class MethodDispatcher(FunctionDispatcher):
    """ Multiple dispatch for methods

    This object dispatch call to method by its class and arguments types.
    Usually it is produced by :func:`.multimethod` decorator.

    You should not manually create objects of this type.
    """

    def __init__(self, argspec, params_arity):
        FunctionDispatcher.__init__(self, argspec, params_arity)

        # some data, that should be local to thread of execution
        self.local = threading.local()
        self.local.unbound_rules = []

    def register_unbound_rule(self, func, *argtypes):
        """ Register unbound rule that should be processed by
        ``proceed_unbound_rules`` later."""
        self.local.unbound_rules.append((argtypes, func))

    def proceed_unbound_rules(self, cls):
        """ Process all unbound rule by binding them to ``cls`` type."""
        for argtypes, func in self.local.unbound_rules:
            argtypes = (cls,) + argtypes
            self.override_rule(func, *argtypes)
        self.local.unbound_rules = []

    def __get__(self, obj, cls):
        if obj is None:
            return self
        return types.MethodType(self, obj)

    def when(self, *argtypes):
        """ Register new case for multimethod for ``argtypes``"""

        def make_declaration(meth):
            self.register_unbound_rule(meth, *argtypes)
            return self

        return make_declaration

    def override(self, *argtypes):
        """ Decorator for overriding case for ``argtypes``"""
        return self.when(*argtypes)

    @property
    def otherwise(self):
        """ Decorator which registeres "catch-all" case for multimethod"""

        def make_declaration(func):
            self.register_unbound_rule(func, [object] * self.params_arity)
            return self

        return make_declaration


def arity(argspec):
    """ Determinal positional arity of argspec."""
    args = argspec.args if argspec.args else []
    defaults = argspec.defaults if argspec.defaults else []
    return len(args) - len(defaults)


def is_equalent_argspecs(left, right):
    """ Check argspec equalence."""

    return tuple(x and len(x) or 0 for x in left[:4]) == tuple(
        x and len(x) or 0 for x in right[:4]
    )


def _make_dispatcher(dispacther_cls, func, params_arity):
    argspec = inspect.getfullargspec(func)
    wrapper = functools.wraps(func)
    dispatcher = wrapper(dispacther_cls(argspec, params_arity))
    return dispatcher
