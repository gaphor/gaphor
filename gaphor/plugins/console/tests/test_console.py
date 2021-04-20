from gi.repository import Gdk, GLib

from gaphor.plugins.console.console import GTKInterpreterConsole, Help, main


class KeyEvent:
    def __init__(self, keyval, state=0):
        self.keyval = keyval
        self.state = state


class DummyWriter:
    def __init__(self):
        self.text = ""

    def write(self, s):
        self.text = self.text + s

    def __enter__(self):
        return self

    def __exit__(self, _type, _value, _traceback):
        pass


def iteration():
    ctx = GLib.main_context_default()
    while ctx.pending():
        ctx.iteration(False)


def test_console_opening():
    main(main_loop=False)
    iteration()


def test_help():
    writer = DummyWriter()
    help = Help(writer)

    help()

    assert "Usage: help(object)" in writer.text


def console_text(console):
    buffer = console.text.get_buffer()
    return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)


def test_history():
    console = GTKInterpreterConsole(locals={})
    console.history.append("my_history()")

    console.key_pressed(console, Gdk.keyval_from_name("Up"), -1, 0)
    text = console_text(console)

    assert ">>> my_history()" in text


def test_deep_history():
    console = GTKInterpreterConsole(locals={})
    console.history.append("deepest()")
    console.history.append("deeper()")
    console.history.append("deep()")

    console.key_pressed(console, Gdk.keyval_from_name("Up"), -1, 0)
    console.key_pressed(console, Gdk.keyval_from_name("Up"), -1, 0)
    console.key_pressed(console, Gdk.keyval_from_name("Up"), -1, 0)
    console.key_pressed(console, Gdk.keyval_from_name("Down"), -1, 0)
    text = console_text(console)

    assert ">>> deeper()" in text


def test_run_line():
    console = GTKInterpreterConsole(locals={})

    console.buffer.append("help")
    console.key_pressed(console, Gdk.keyval_from_name("Return"), -1, 0)

    text = console_text(console)

    assert "Usage: help(object)" in text
