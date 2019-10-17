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
        self,
        name,
        label=None,
        tooltip=None,
        icon_name=None,
        shortcut=None,
        state=None,
        **kwargs,
    ):
        self.scope, self.name = name.split(".", 2) if "." in name else ("win", name)
        self.label = label
        self.tooltip = tooltip
        self.icon_name = icon_name
        self.shortcut = shortcut
        self.state = state
        self.arg_type = None
        self.__dict__.update(kwargs)

    def __call__(self, func):
        type_hints = get_type_hints(func)
        if len(type_hints) == 1:
            # assume the first argument (exclusing self) is our parameter
            self.arg_type = next(iter(type_hints.values()))
        func.__action__ = self
        return func


class radio_action(action):
    """
    Radio buttons take a list of names, a list of labels and a list of
    tooltips (and optionally, a list of icon names).
    The callback function should have an extra value property, which is
    given the index number of the activated radio button action.
    """

    names: Sequence[str]
    labels: Sequence[Optional[str]]
    tooltips: Sequence[Optional[str]]
    icon_names: Sequence[Optional[str]]
    shortcuts: Sequence[Optional[str]]
    active: int

    def __init__(
        self,
        names,
        labels=None,
        tooltips=None,
        icon_names=None,
        shortcuts=None,
        active=0,
    ):
        super().__init__(
            names[0],
            names=names,
            labels=labels,
            tooltips=tooltips,
            icon_names=icon_names,
            shortcuts=shortcuts,
            active=active,
        )


def is_action(func):
    return hasattr(func, "__action__")


if __name__ == "__main__":
    import doctest

    doctest.testmod()
