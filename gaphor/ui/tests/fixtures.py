from gi.repository import GLib


def iterate_until(condition, timeout=5):
    sentinel = False

    def check_condition():
        nonlocal sentinel
        if condition():
            sentinel = True
        return GLib.SOURCE_REMOVE if sentinel else GLib.SOURCE_CONTINUE

    def do_timeout():
        nonlocal sentinel
        sentinel = True
        return GLib.SOURCE_REMOVE

    GLib.idle_add(check_condition, priority=GLib.PRIORITY_LOW)
    timeout_id = GLib.timeout_add(interval=timeout * 1_000, function=do_timeout)

    ctx = GLib.main_context_default()
    while ctx.pending():
        if sentinel:
            break
        ctx.iteration(False)

    if not sentinel:
        GLib.source_remove(timeout_id)
