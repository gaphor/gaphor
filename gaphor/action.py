"""Support for actions in generic files.

"""

from typing import Optional, Sequence, get_type_hints
import platform


_primary = "⌘" if platform.system() == "Darwin" else "Ctrl"


def primary():
    global _primary
    return _primary


class action:
    """
    Decorator. Turns a regular function (/method) into a full blown
    Action class.

    >>> class A:
    ...     @action(name="my_action", label="my action")
    ...     def myaction(self):
    ...         print('action called')
    >>> a = A()
    >>> a.myaction()
    action called
    >>> is_action(a.myaction)
    True
    >>> for method in dir(A):
    ...     if is_action(getattr(A, method, None)):
    ...         print(method)
    myaction
    >>> A.myaction.__action__.name
    'my_action'
    >>> A.myaction.__action__.label
    'my action'
    """

    def __init__(
        self, name, label=None, tooltip=None, icon_name=None, shortcut=None, state=None
    ):
        self.scope, self.name = name.split(".", 2) if "." in name else ("win", name)
        self.label = label
        self.tooltip = tooltip
        self.icon_name = icon_name
        self.shortcut = shortcut
        self.state = state
        self.arg_type = None

    def __call__(self, func):
        type_hints = get_type_hints(func)
        if len(type_hints) == 1:
            # assume the first argument (exclusing self) is our parameter
            self.arg_type = next(iter(type_hints.values()))
        func.__action__ = self
        return func


def is_action(func):
    return hasattr(func, "__action__")
