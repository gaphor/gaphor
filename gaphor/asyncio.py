"""AsyncIO support for Gaphor.

This module allows to keep track of
async tasks.
"""

import asyncio
import contextlib

from gi.events import GLibEventLoopPolicy
from gi.repository import GLib


@contextlib.contextmanager
def glib_event_loop_policy():
    original = asyncio.get_event_loop_policy()
    policy = GLibEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    try:
        yield policy
    finally:
        asyncio.set_event_loop_policy(original)


_background_tasks = set()


def create_background_task(coro) -> asyncio.Task:
    """Create and track a task.

    Normally tasks are weak-referenced by asyncio.
    We keep track of them, so they can be completed
    before GC kicks in.
    """
    task = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)
    return task


async def gather_background_tasks():
    """Gather (run) all background tasks.

    This is sort of a stop gap solution since not
    all code is async/await aware.
    """
    if _background_tasks:
        await asyncio.gather(*_background_tasks)


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
