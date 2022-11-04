"""Adapters for the Property Editor.

To register property pages implemented in this module, it is imported in
gaphor.adapter package.
"""

from __future__ import annotations

import abc
from typing import Callable, Iterable

import gaphas.item
from gaphas.segment import Segment

from gaphor.core import transactional
from gaphor.core.modeling import Element
from gaphor.i18n import translated_ui_string
from gaphor.lazygi import Gtk


def new_resource_builder(package, property_pages="propertypages"):
    def new_builder(*object_ids, signals=None):
        if Gtk.get_major_version() == 3:
            builder = Gtk.Builder()
            ui_file = f"{property_pages}.glade"
        else:
            builder = Gtk.Builder(signals)
            ui_file = f"{property_pages}.ui"

        builder.add_objects_from_string(
            translated_ui_string(package, ui_file), object_ids
        )
        if signals and Gtk.get_major_version() == 3:
            builder.connect_signals(signals)
        return builder

    return new_builder


new_builder = new_resource_builder("gaphor.diagram")


class _PropertyPages:
    """Generic handler for property pages.

    Property pages are collected on type.
    """

    def __init__(self) -> None:
        self.pages: list[
            tuple[type[Element], Callable[[Element], PropertyPageBase]]
        ] = []

    def register(self, subject_type):
        def reg(func):
            self.pages.append((subject_type, func))
            return func

        return reg

    def __call__(self, subject):
        for subject_type, func in self.pages:
            if isinstance(subject, subject_type):
                yield func(subject)


PropertyPages = _PropertyPages()


class PropertyPageBase(metaclass=abc.ABCMeta):
    """A property page which can display itself in a notebook."""

    order = 100  # Order number, used for ordered display

    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def construct(self):
        """Create the page (Gtk.Widget) that belongs to the Property page.

        Returns the page's toplevel widget (Gtk.Widget).
        """


@transactional
def on_text_cell_edited(renderer, path, value, model, col=0):
    """Update editable tree model based on fresh user input."""

    iter = model.get_iter(path)
    model.update(iter, col, value)


@transactional
def on_bool_cell_edited(renderer, path, model, col):
    """Update editable tree model based on fresh user input."""

    iter = model.get_iter(path)
    model.update(iter, col, renderer.get_active())


def combo_box_text_auto_complete(
    combo: Gtk.ComboBoxText, data_iterator: Iterable[tuple[str, str]], text: str = ""
) -> None:
    for id, name in data_iterator:
        if name:
            combo.append(id, name)

    completion = Gtk.EntryCompletion()
    completion.set_model(combo.get_model())
    completion.set_minimum_key_length(1)
    completion.set_text_column(0)

    entry = combo.get_child()
    entry.set_completion(completion)
    if text:
        entry.set_text(text)


def help_link(builder, help_widget, popover):
    """Show the help popover for a `Help` link in the property page.

    GTK4 only.
    """

    def on_activate(*_args):
        builder.get_object(popover).show()

    help = builder.get_object(help_widget)
    help.set_accessible_role(Gtk.AccessibleRole.BUTTON)
    click_handler = Gtk.GestureClick.new()
    click_handler.connect("released", on_activate)
    help.add_controller(click_handler)


def handler_blocking(widget, event_name, widget_handler):
    changed_id = widget.connect(event_name, widget_handler)

    def handler_wrapper(func):
        def _handler(event):
            widget.handler_block(changed_id)
            func(event)
            widget.handler_unblock(changed_id)

        return _handler

    return handler_wrapper


@PropertyPages.register(gaphas.item.Line)
class LineStylePage(PropertyPageBase):
    """Basic line style properties: color, orthogonal, etc."""

    order = 400

    def __init__(self, item):
        super().__init__()
        self.item = item
        self.horizontal_button: Gtk.Button

    def construct(self):
        builder = new_builder(
            "line-editor",
            signals={
                "rectilinear-changed": (self._on_orthogonal_change,),
                "orientation-changed": (self._on_horizontal_change,),
            },
        )

        rectilinear_button = builder.get_object("line-rectilinear")
        horizontal_button = builder.get_object("flip-orientation")

        self.horizontal_button = horizontal_button

        rectilinear_button.set_active(self.item.orthogonal)
        horizontal_button.set_active(self.item.horizontal)
        horizontal_button.set_sensitive(self.item.orthogonal)

        return builder.get_object("line-editor")

    @transactional
    def _on_orthogonal_change(self, button):
        if len(self.item.handles()) < 3:
            line_segment = Segment(self.item, self.item.diagram)
            line_segment.split_segment(0)
        active = button.get_active()
        self.item.orthogonal = active
        self.item.diagram.update_now((self.item,))
        self.horizontal_button.set_sensitive(active)

    @transactional
    def _on_horizontal_change(self, button):
        self.item.horizontal = button.get_active()
        self.item.diagram.update_now((self.item,))


@PropertyPages.register(Element)
class NotePropertyPage(PropertyPageBase):
    """A facility to add a little note/remark."""

    order = 300

    def __init__(self, subject):
        self.subject = subject
        self.watcher = subject and subject.watcher()

    def construct(self):
        subject = self.subject

        if not subject:
            return

        builder = new_builder("note-editor")
        text_view = builder.get_object("note")

        buffer = Gtk.TextBuffer()
        if subject.note:
            buffer.set_text(subject.note)
        text_view.set_buffer(buffer)

        @handler_blocking(buffer, "changed", self._on_body_change)
        def handler(event):
            if not text_view.props.has_focus:
                buffer.set_text(event.new_value or "")

        self.watcher.watch("note", handler)
        text_view.connect("destroy", self.watcher.unsubscribe_all)

        return builder.get_object("note-editor")

    @transactional
    def _on_body_change(self, buffer):
        self.subject.note = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), False
        )
