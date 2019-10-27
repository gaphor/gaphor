from gi.repository import Gdk, Gtk
from gaphor.plugins.console.console import main, GTKInterpreterConsole, Help


class KeyEvent:
    def __init__(self, keyval, state=0):
        self.keyval = keyval
        self.state = state


def test_console_opening():
    main(main_loop=False)
    Gtk.main_iteration()


def test_help():
    help = Help()

    assert help() == "Usage: help(object)"


def test_help_on_object(capsys):
    help = Help()

    help(str)
    captured = capsys.readouterr()

    assert "|" in captured.out


def console_text(console):
    buffer = console.text.get_buffer()
    return buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), False)


def test_history():
    console = GTKInterpreterConsole()
    console.history.append("my_history()")

    console.key_pressed(console, KeyEvent(Gdk.keyval_from_name("Up")))
    text = console_text(console)

    assert ">>> my_history()" in text


def test_deep_history():
    console = GTKInterpreterConsole()
    console.history.append("deepest()")
    console.history.append("deeper()")
    console.history.append("deep()")

    console.key_pressed(console, KeyEvent(Gdk.keyval_from_name("Up")))
    console.key_pressed(console, KeyEvent(Gdk.keyval_from_name("Up")))
    console.key_pressed(console, KeyEvent(Gdk.keyval_from_name("Up")))
    console.key_pressed(console, KeyEvent(Gdk.keyval_from_name("Down")))
    text = console_text(console)

    assert ">>> deeper()" in text


def test_run_line():
    console = GTKInterpreterConsole()

    console.buffer.append("help")
    console.key_pressed(console, KeyEvent(Gdk.keyval_from_name("Return")))

    text = console_text(console)

    assert "Usage: help(object)" in text
