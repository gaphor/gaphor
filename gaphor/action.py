"""Support for actions in generic files."""

from __future__ import annotations

import asyncio
import inspect
import logging
from collections.abc import Callable, Iterator
from typing import Any, get_type_hints

log = logging.getLogger(__name__)


class action:
    """Decorator. Turns a regular function (/method) into a full blown Action
    class.

    >>> class A:
    ...     @action(name="my_action", label="my action")
    ...     def myaction(self):
    ...         print("action called")
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

    def __init__(  # type: ignore[explicit-any]
        self,
        name,
        label: str | None = None,
        tooltip: str | None = None,
        icon_name: str | None = None,
        shortcut: str | tuple[str, ...] | None = None,
        state: bool | Callable[[Any], bool | str] | None = None,
    ):
        self.scope: str
        self.name: str
        self.scope, self.name = name.split(".", 2) if "." in name else ("win", name)
        self.label = label
        self.tooltip = tooltip
        self.icon_name = icon_name
        self.shortcut = shortcut
        self.state = state
        self.arg_type = None
        self.task: asyncio.Task | None = None

    @property
    def detailed_name(self) -> str:
        return f"{self.scope}.{self.name}"

    @property
    def shortcuts(self) -> Iterator[str]:
        s = self.shortcut
        if isinstance(s, str):
            yield s
        elif s:
            yield from s

    def __call__(self, func):
        type_hints = get_type_hints(func)
        if "return" in type_hints:
            del type_hints["return"]
        if type_hints:
            # assume the first argument (excluding self) is our parameter
            self.arg_type = next(iter(type_hints.values()))

        if inspect.iscoroutinefunction(func):

            def async_action(*args) -> None:
                if self.task:
                    log.warning("Action %s is already running", self.detailed_name)
                    return

                coro = func(*args)
                task = asyncio.create_task(coro)
                self.task = task
                task.add_done_callback(self._task_done)

            async_action.__action__ = self  # type: ignore[attr-defined]
            return async_action

        else:
            func.__action__ = self
            return func

    def _task_done(self, task: asyncio.Task) -> None:
        self.task = None


def is_action(func):
    return hasattr(func, "__action__")
