"""AsyncIO support for Gaphor.

This module allows to keep track of
async tasks.
"""

import asyncio
import contextlib
from collections.abc import Coroutine

from gi.events import GLibEventLoopPolicy
from gi.repository import GLib


class TaskOwner:
    """Mixin that allows an object to manage an asyncio task.

    The TaskOwner allows for managing one (!) task at a time.
    """

    def __init__(self):
        self._background_task: asyncio.Task | None = None

    def create_background_task(self, coro: Coroutine) -> asyncio.Task:
        assert self._background_task is None or self._background_task.done()
        task = asyncio.create_task(coro)
        self._background_task = task

        def task_done(task):
            assert self._background_task is task
            self._background_task = None

        task.add_done_callback(task_done)
        return task

    def cancel_background_task(self) -> bool:
        return (self._background_task is not None) and self._background_task.cancel()

    async def gather_background_task(self):
        if self._background_task:
            await asyncio.gather(self._background_task)


async def response_from_adwaita_dialog(dialog, window) -> str:
    response = asyncio.get_running_loop().create_future()

    def response_cb(_dialog, answer):
        response.set_result(answer)

    dialog.connect("response", response_cb)
    dialog.present(window)

    answer = await response
    assert isinstance(answer, str)

    return answer


# Notes for PyGObject 3.52:
# * `glib_event_loop_policy` can be removed: use `with GLibEventLoopPolicy()`.
# * `sleep` can be removed: use `task.set_priority(GLib.PRIORITY_LOW)`.


@contextlib.contextmanager
def glib_event_loop_policy():
    original = asyncio.get_event_loop_policy()
    policy = GLibEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    try:
        yield policy
    finally:
        asyncio.set_event_loop_policy(original)


def sleep(delay, result=None, priority=GLib.PRIORITY_LOW):
    """Prioritizable version of asyncio.sleep().

    Normal asyncio.sleep() runs with priority DEFAULT,
    which blocks the UI. This sleep has a configurable
    priority.
    """
    if GLib.main_depth() == 0:
        return asyncio.sleep(delay, result)

    f: asyncio.Future = asyncio.Future()

    def timeout_func(*args):
        f.set_result(result)
        return GLib.SOURCE_REMOVE

    GLib.timeout_add(int(delay * 1000), timeout_func, f, priority=priority)
    return f
