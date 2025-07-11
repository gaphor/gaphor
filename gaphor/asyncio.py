"""AsyncIO support for Gaphor.

This module allows to keep track of
async tasks.
"""

import asyncio

from gi.repository import GLib

# Notes for PyGObject 3.52:
# * `sleep` can be removed: use `task.set_priority(GLib.PRIORITY_LOW)`.


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
