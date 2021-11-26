#!/usr/bin/env python

#  GTK Interactive Console
#  (C) 2003, Jon Anderson
#  See www.python.org/2.2/license.html for
#  license details.
#
#  Took some good ideas from the GEdit Python Console:
#  https://gitlab.gnome.org/GNOME/gedit/-/blob/master/plugins/pythonconsole/pythonconsole/console.py
#  Licensed under GPL


import code
import sys
import textwrap
from typing import Dict, List

import jedi
from gi.repository import Gdk, GLib, Gtk, Pango

from gaphor.i18n import gettext

banner = gettext(
    """\
Gaphor Interactive Python Console
{version}
Type "help" for more information.
"""
).format(version=sys.version)


def _text_tag(name, **properties):
    tag = Gtk.TextTag.new(name)
    for prop, val in properties.items():
        tag.set_property(prop, val)
    return name, tag


prompt = {
    "ps1": ">>> ",
    "ps2": "... ",
}

style = dict(
    [
        _text_tag("banner", foreground="#77767b"),
        _text_tag("ps1", editable=False),
        _text_tag("ps2", foreground="#77767b", editable=False),
        _text_tag("stdout", editable=False),
        _text_tag(
            "stderr", style=Pango.Style.ITALIC, foreground="#cc0000", editable=False
        ),
    ]
)


def docstring_dedent(docstr: str) -> str:
    if docstr.startswith(" "):
        return textwrap.dedent(docstr)

    first_line, remaining_text = docstr.split("\n", 1)

    return "\n".join([first_line, textwrap.dedent(remaining_text)])


class Help:
    def __init__(self, writer, locals={}):
        self._writer = writer
        self._locals = locals

    def __call__(self, obj=None):
        helptext = docstring_dedent(obj.__doc__ if obj else str(self))
        with self._writer as writer:
            writer.write("\n")
            writer.write(textwrap.indent(helptext, prefix="  "))
            writer.write("\n" if helptext.endswith("\n") else "\n\n")

    def __str__(self):
        intro = textwrap.dedent(
            """\

        Usage: help(object)

        The following functions/variables are defined:
        """
        )

        members = "\n".join(
            f"- {key}" for key in self._locals.keys() if not key.startswith("_")
        )

        return textwrap.indent(intro + members + "\n", prefix="  ")

    def __repr__(self):
        return str(self)


class TextViewWriter:
    """A Multiplexing output stream.

    It can replace another stream, and tee output to the original stream
    and too a GTK textview.
    """

    def __init__(self, name, view):
        self.name = name
        self.out = getattr(sys, name)
        self.view = view

    def write(self, text):
        buffer = self.view.get_buffer()
        end = buffer.get_end_iter()
        buffer.insert_with_tags(end, text, style[self.name])

    def __enter__(self):
        setattr(sys, self.name, self)
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        setattr(sys, self.name, self.out)


class GTKInterpreterConsole(Gtk.ScrolledWindow):
    """An Interactive Console for GTK.

    It's an actual widget, so it can be dropped in just about anywhere.
    """

    __gtype_name__ = "GTKInterpreterConsole"

    def __init__(self, locals: Dict[str, object], banner=banner):
        Gtk.ScrolledWindow.__init__(self)

        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.text = Gtk.TextView()
        self.text.set_wrap_mode(True)
        self.text.set_monospace(True)

        self.interpreter = code.InteractiveInterpreter(locals)
        self.locals = locals

        self.buffer: List[str] = []
        self.history: List[str] = []
        self.banner = banner

        if Gtk.get_major_version() == 3:
            self.text_controller = Gtk.EventControllerKey.new(self.text)
        else:
            self.text_controller = Gtk.EventControllerKey.new()
            self.text.add_controller(self.text_controller)

        self.text_controller.connect("key-pressed", self.key_pressed)

        self.current_history = -1

        buffer = self.text.get_buffer()
        buffer.create_mark("input", buffer.get_end_iter(), True)

        for tag in style.values():
            buffer.get_tag_table().add(tag)

        self.stdout = TextViewWriter("stdout", self.text)
        self.stderr = TextViewWriter("stderr", self.text)

        self.current_prompt = "ps1"
        locals["help"] = Help(self.stdout, locals)

        self.write(self.banner, style["banner"])
        self.prompt()

        if Gtk.get_major_version() == 3:
            self.add(self.text)
            self.text.show()
        else:
            self.set_child(self.text)

    def reset_buffer(self):
        self.buffer = []

    def prompt(self):
        self.write(prompt[self.current_prompt], style[self.current_prompt])
        self.move_input_mark()
        GLib.idle_add(self.scroll_to_end)

    def write(self, text, style=None):
        buffer = self.text.get_buffer()
        start, end = buffer.get_bounds()
        if style:
            buffer.insert_with_tags(end, text, style)
        else:
            buffer.insert(end, text)

        buffer.place_cursor(buffer.get_end_iter())

    def move_input_mark(self):
        buffer = self.text.get_buffer()
        input_mark = buffer.get_mark("input")
        buffer.move_mark(input_mark, buffer.get_end_iter())

    def scroll_to_end(self):
        buffer = self.text.get_buffer()
        input_mark = buffer.get_mark("input")
        self.text.scroll_to_mark(input_mark, 0, True, 1, 1)
        return False

    def push(self, line):
        self.buffer.append(line)
        if len(line) > 0:
            self.history.append(line)

        source = "\n".join(self.buffer)

        with self.stdout, self.stderr:
            more = self.interpreter.runsource(source, "<<console>>")

        if not more:
            self.reset_buffer()

        return more

    def key_pressed(self, widget, keyval, keycode, state):
        if keyval == Gdk.keyval_from_name("Return"):
            return self.execute_line()
        if keyval == Gdk.keyval_from_name("Tab"):
            return self.complete_line()

        if keyval == Gdk.keyval_from_name("Up"):
            self.current_history = self.current_history - 1
            self.current_history = max(self.current_history, -len(self.history))
            return self.show_history()
        if keyval == Gdk.keyval_from_name("Down"):
            self.current_history = self.current_history + 1
            self.current_history = min(self.current_history, 0)
            return self.show_history()

        ctrl = state & Gdk.ModifierType.CONTROL_MASK
        if (keyval == Gdk.keyval_from_name("Home")) or (ctrl and keyval == Gdk.KEY_a):
            line_count = self.text.get_buffer().get_line_count() - 1
            start = self.text.get_buffer().get_iter_at_line_offset(line_count, 4)
            self.text.get_buffer().place_cursor(start)
            return True

        if ctrl and keyval == Gdk.KEY_e:
            end = self.text.get_buffer().get_end_iter()
            self.text.get_buffer().place_cursor(end)
            return True

        if (
            ctrl
            and keyval == Gdk.KEY_c
            and not self.text.get_buffer().get_selection_bounds()
        ):
            self.write("^C\n")
            self.reset_buffer()
            self.current_prompt = "ps1"
            self.prompt()
            return True

        return False

    def show_history(self):
        if self.current_history != 0:
            self.replace_line(self.history[self.current_history])

        return True

    def current_line(self):
        start, end = self.current_line_bounds()
        return self.text.get_buffer().get_text(start, end, True)

    def current_line_bounds(self):
        buffer = self.text.get_buffer()
        input_mark = buffer.get_mark("input")
        start = buffer.get_iter_at_mark(input_mark)
        end = buffer.get_end_iter()
        return start, end

    def replace_line(self, txt):
        start, end = self.current_line_bounds()
        self.text.get_buffer().delete(start, end)
        self.write(txt)

    def execute_line(self):
        line = self.current_line()

        self.write("\n")

        more = self.push(line)

        self.current_prompt = "ps2" if more else "ps1"
        self.prompt()
        self.current_history = 0

        return True

    def complete_line(self):
        line = self.current_line()
        source = "\n".join(self.buffer + [line])
        script = jedi.Interpreter(source, [self.locals])
        completions = script.complete()

        if len(completions) > 1:
            max_len = max(map(lambda c: len(c.name), completions)) + 2
            per_line = 76 // max_len
            for i, c in enumerate(completions):
                if i % per_line == 0:
                    self.write("\n")
                self.write(c.name, style["ps1"])
                self.write(" " * (max_len - len(c.name)), style["ps1"])
            self.write("\n")
            self.prompt()
            self.write(line)
        elif len(completions) == 1:
            self.write(completions[0].complete)

        return True


def main(main_loop=True):
    w = Gtk.ApplicationWindow()
    w.set_default_size(640, 480)
    console = GTKInterpreterConsole(locals())

    def key_event(widget, keyval, keycode, state):
        if keyval == Gdk.KEY_d and state & Gdk.ModifierType.CONTROL_MASK:
            app.quit()
        return False

    w.connect("destroy", lambda w: app.quit())
    console.text_controller.connect("key-pressed", key_event)

    if Gtk.get_major_version() == 3:
        w.add(console)
        w.show_all()
    else:
        w.set_child(console)
        w.show()

    if main_loop:

        def on_activate(app):
            app.add_window(w)

        app = Gtk.Application.new("org.gaphor.Console", 0)
        app.connect("activate", on_activate)
        app.run()


if __name__ == "__main__":
    main()
