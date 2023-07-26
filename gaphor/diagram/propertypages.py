"""Adapters for the Property Editor.

To register property pages implemented in this module, it is imported in
gaphor.adapter package.
"""

from __future__ import annotations

import abc
from typing import Callable, List, Tuple, Type

import gaphas.item
from gaphas.segment import Segment
from gi.repository import GObject, Gtk

from gaphor.core import transactional
from gaphor.core.modeling import Diagram, Element, Presentation
from gaphor.i18n import translated_ui_string


class LabelValue(GObject.Object):
    __gtype_name__ = "LabelValue"

    def __init__(self, label, value):
        super().__init__()
        self._label = label
        self._value = value

    @GObject.Property(type=str)
    def label(self):
        return self._label

    @property
    def value(self):
        return self._value


def new_resource_builder(package, property_pages="propertypages"):
    def new_builder(*object_ids, signals=None):
        builder = Gtk.Builder(signals)
        builder.add_objects_from_string(
            translated_ui_string(package, f"{property_pages}.ui"), object_ids
        )
        return builder

    return new_builder


new_builder = new_resource_builder("gaphor.diagram")


class _PropertyPages:
    """Generic handler for property pages.

    Property pages are collected on type.
    """

    def __init__(self) -> None:
        self.pages: List[
            Tuple[Type[Element], Callable[[Element], PropertyPageBase]]
        ] = []

    def register(self, subject_type, func=None):
        def reg(func):
            self.pages.append((subject_type, func))
            return func

        return reg(func) if func else reg

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
    def construct(self) -> Gtk.Widget | None:
        """Create the page (Gtk.Widget) that belongs to the Property page.

        Returns the page's toplevel widget (Gtk.Widget).
        """


class EditableTreeModel(Gtk.ListStore):
    """Editable GTK tree model based on ListStore model.

    Every row is represented by a list of editable values. Last column
    contains an object, which is being edited (this column is not
    displayed). When editable value in first column is set to empty string
    then object is deleted.

    Last row is empty and contains no object to edit. It allows to enter
    new values.
    """

    def __init__(self, item, cols):
        """Create new model.

        Args:
          item (Presentation): diagram item owning tree model
          cols (tuple): model column types, defaults to [str, object]
        """
        super().__init__(*cols)
        self._item = item

        for data in self.get_rows():
            self.append(data)
        self._add_empty()
        self.connect_after("row-inserted", self.on_row_inserted)

    def on_row_inserted(self, model, path, iter):
        """This method is called when new elements are added and when a row is
        moved via DnD."""
        new_order = [row[-1] for row in self if row[-1]]
        self.sync_model(new_order)

    def get_rows(self):
        """Return rows to be edited.

        Last column has to contain object being edited.
        """

        raise NotImplementedError

    def create_object(self):
        """Create new object."""
        raise NotImplementedError

    def set_object_value(self, row, col, value):
        """Update row's column with a value."""
        raise NotImplementedError

    def swap_objects(self, o1, o2):
        """Swap two objects.

        If objects are swapped, then return ``True``.
        """
        raise NotImplementedError

    def _get_object(self, iter):
        """Get object from ``iter``."""
        path = self.get_path(iter)
        return self[path][-1]

    def swap(self, a, b):
        """
        Swap two list rows.
        Parameters:
        - a: path to first row
        - b: path to second row
        """
        if not (a and b):
            return
        o1 = self[a][-1]
        o2 = self[b][-1]
        if o1 and o2 and self.swap_objects(o1, o2):
            super().swap(a, b)

    def _add_empty(self):
        """Add empty row to the end of the model."""
        self.append([None] * self.get_n_columns())

    @transactional
    def update(self, iter, col, value):
        row = self[iter]

        if col == 0 and not value and row[-1]:
            # delete row and object if text of first column is empty
            self.remove(iter)

        elif col == 0 and value and not row[-1]:
            # create new object
            obj = self.create_object()
            row[-1] = obj
            self.set_object_value(row, col, value)
            self._add_empty()

        elif row[-1]:
            self.set_object_value(row, col, value)

    def remove(self, iter):
        """Remove object from GTK model and destroy it."""
        if obj := self._get_object(iter):
            obj.unlink()
            return super().remove(iter)
        else:
            return iter


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


def help_link(builder, help_widget, popover):
    """Show the help popover for a `Help` link in the property page."""

    def on_activate(*_args):
        builder.get_object(popover).set_visible(True)

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


def _do_unparent(widget, _pspec, watcher):
    if not widget.props.parent:
        watcher.unsubscribe_all()


def unsubscribe_all_on_destroy(widget, watcher):
    widget.connect("notify::parent", _do_unparent, watcher)
    return widget


@PropertyPages.register(Diagram)
class NamePropertyPage(PropertyPageBase):
    """An adapter which works for any named item view.

    It also sets up a table view which can be extended.
    """

    order = 10

    def __init__(self, subject):
        assert subject is None or hasattr(subject, "name")
        super().__init__()
        self.subject = subject
        self.watcher = subject.watcher() if subject else None

    def construct(self):
        if not self.subject:
            return

        assert self.watcher
        builder = new_builder(
            "name-editor",
        )

        subject = self.subject

        entry = builder.get_object("name-entry")
        entry.set_text(subject and subject.name or "")

        @handler_blocking(entry, "changed", self._on_name_changed)
        def handler(event):
            if event.element is subject and event.new_value != entry.get_text():
                entry.set_text(event.new_value or "")

        self.watcher.watch("name", handler)

        return unsubscribe_all_on_destroy(
            builder.get_object("name-editor"), self.watcher
        )

    @transactional
    def _on_name_changed(self, entry):
        if self.subject.name != entry.get_text():
            self.subject.name = entry.get_text()


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
    def _on_orthogonal_change(self, button, gparam):
        if len(self.item.handles()) < 3:
            line_segment = Segment(self.item, self.item.diagram)
            line_segment.split_segment(0)
        active = button.get_active()
        self.item.orthogonal = active
        self.item.diagram.update_now((self.item,))
        self.horizontal_button.set_sensitive(active)

    @transactional
    def _on_horizontal_change(self, button, gparam):
        self.item.horizontal = button.get_active()
        self.item.diagram.update_now((self.item,))


@PropertyPages.register(Element)
class NotePropertyPage(PropertyPageBase):
    """A facility to add a little note/remark."""

    order = 300

    def __init__(self, subject):
        self.subject = subject.subject if isinstance(subject, Presentation) else subject
        self.watcher = self.subject and self.subject.watcher()

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
