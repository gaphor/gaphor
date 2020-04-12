"""
Adapters for the Property Editor.

To register property pages implemented in this module, it is imported in
gaphor.adapter package.

# TODO: make all labels align top-left
# Add hidden columns for list stores where i can put the actual object
# being edited.

TODO:
 - stereotypes
 - association / association ends.
 - Follow HIG guidelines:
   * Leave a 12-pixel border between the edge of the window and
     the nearest controls.
   * Leave a 12-pixel horizontal gap between a control and its label. (The gap
     may be bigger for other controls in the same group, due to differences in
     the lengths of the labels.)
   * Labels must be concise and make sense when taken out of context.
     Otherwise, users relying on screenreaders or similar assistive
     technologies will not always be able to immediately understand the
     relationship between a control and those surrounding it.
   * Assign access keys to all editable controls. Ensure that using the access
     key focuses its associated control.
"""

import abc
import importlib
from typing import Callable, Dict, List, Tuple, Type

import gaphas.item
from gaphas.decorators import AsyncIO
from gaphas.segment import Segment
from gi.repository import Gdk, GObject, Gtk

from gaphor import UML
from gaphor.core import gettext, transactional
from gaphor.core.modeling.element import DummyEventWatcher, Element


def new_builder(*object_ids):
    builder = Gtk.Builder()
    builder.set_translation_domain("gaphor")
    with importlib.resources.path(
        "gaphor.diagram", "propertypages.glade"
    ) as glade_file:
        builder.add_objects_from_file(str(glade_file), object_ids)
    return builder


class _PropertyPages:
    """
    Generic handler for property pages.

    Property pages are collected on type.
    """

    def __init__(self) -> None:
        self.pages: List[
            Tuple[Type[Element], Callable[[Element], PropertyPageBase]]
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
    """
    A property page which can display itself in a notebook
    """

    order = 100  # Order number, used for ordered display

    def __init__(self):
        super().__init__()

    @abc.abstractmethod
    def construct(self):
        """
        Create the page (Gtk.Widget) that belongs to the Property page.

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

    When model is edited, then item is requested to be updated on canvas.

    Attributes:
    - _item: diagram item owning tree model
    """

    def __init__(self, item, cols=None):
        """Create new model.

        Parameters:
        - _item: diagram item owning tree model
        - cols: model columns, defaults to [str, object]
        """

        if cols is None:
            cols = (str, object)
        super().__init__(*cols)
        self._item = item

        for data in self._get_rows():
            self.append(data)
        self._add_empty()

    def _get_rows(self):
        """Return rows to be edited.

        Last column has to contain object being edited.
        """

        raise NotImplementedError

    def _create_object(self):
        """
        Create new object.
        """
        raise NotImplementedError

    def _set_object_value(self, row, col, value):
        """
        Update row's column with a value.
        """
        raise NotImplementedError

    def _swap_objects(self, o1, o2):
        """
        Swap two objects. If objects are swapped, then return ``True``.
        """
        raise NotImplementedError

    def _get_object(self, iter):
        """
        Get object from ``iter``.
        """
        path = self.get_path(iter)
        return self[path][-1]

    def swap(self, a, b):
        """
        Swap two list rows.
        Parameters:
        - a: path to first row
        - b: path to second row
        """
        if not a or not b:
            return
        o1 = self[a][-1]
        o2 = self[b][-1]
        if o1 and o2 and self._swap_objects(o1, o2):
            # self._item.request_update(matrix=False)
            super().swap(a, b)

    def _add_empty(self):
        """
        Add empty row to the end of the model.
        """
        self.append([None] * self.get_n_columns())

    @transactional
    def update(self, iter, col, value):
        row = self[iter]

        if col == 0 and not value and row[-1]:
            # delete row and object if text of first column is empty
            self.remove(iter)

        elif col == 0 and value and not row[-1]:
            # create new object
            obj = self._create_object()
            row[-1] = obj
            self._set_object_value(row, col, value)
            self._add_empty()

        elif row[-1]:
            self._set_object_value(row, col, value)

    def remove(self, iter):
        """
        Remove object from GTK model and destroy it.
        """
        obj = self._get_object(iter)
        if obj:
            obj.unlink()
            # self._item.request_update(matrix=False)
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


@transactional
def on_keypress_event(tree, event):
    k = Gdk.keyval_name(event.keyval).lower()
    if k in ("backspace", "delete"):
        model, iter = tree.get_selection().get_selected()
        if iter:
            model.remove(iter)
    elif k in ("equal", "plus"):
        model, iter = tree.get_selection().get_selected()
        model.swap(iter, model.iter_next(iter))
        return True
    elif k in ("minus", "underscore"):
        model, iter = tree.get_selection().get_selected()
        model.swap(iter, model.iter_previous(iter))
        return True


class ComboModel(Gtk.ListStore):
    """combo box model.

    Model allows to easily create a combo box with values and their labels,
    for example

        label1  ->  value1
        label2  ->  value2
        label3  ->  value3

    Labels are displayed by combo box and programmer has easy access to
    values associated with given label.

    Attributes:

    - _data: model data
    - _indices: dictionary of values' indices
    """

    def __init__(self, data):
        super().__init__(str)

        self._indices: Dict[Tuple[str, str], int] = {}
        self._data = data

        # add labels to underlying model and store index information
        for i, (label, value) in enumerate(data):
            self.append([label])
            self._indices[value] = i

    def get_index(self, value):
        """
        Return index of a ``value``.
        """
        return self._indices[value]

    def get_value(self, index):
        """
        Get value for given ``index``.
        """
        return self._data[index][1]


@PropertyPages.register(UML.NamedElement)
class NamedElementPropertyPage(PropertyPageBase):
    """An adapter which works for any named item view.

    It also sets up a table view which can be extended.
    """

    order = 10

    NAME_LABEL = gettext("Name")

    def __init__(self, subject: UML.NamedElement):
        super().__init__()
        assert subject is None or isinstance(subject, UML.NamedElement), "%s" % type(
            subject
        )
        self.subject = subject
        self.watcher = subject.watcher() if subject else DummyEventWatcher()

    def construct(self):
        if UML.model.is_metaclass(self.subject):
            return

        builder = new_builder("named-element-editor")

        subject = self.subject
        if not subject:
            return

        entry = builder.get_object("name-entry")
        entry.set_text(subject and subject.name or "")

        def handler(event):
            if event.element is subject and event.new_value is not None:
                entry.set_text(event.new_value)

        if self.watcher:
            self.watcher.watch("name", handler).subscribe_all()

        builder.connect_signals(
            {
                "name-changed": (self._on_name_changed,),
                "name-entry-destroyed": (self.watcher.unsubscribe_all,),
            }
        )
        return builder.get_object("named-element-editor")

    @transactional
    def _on_name_changed(self, entry):
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
        builder = new_builder("line-editor")

        rectilinear_button = builder.get_object("line-rectilinear")
        rectilinear_button.set_active(self.item.orthogonal)

        horizontal_button = builder.get_object("flip-orientation")
        horizontal_button.set_active(self.item.horizontal)
        horizontal_button.set_sensitive(self.item.orthogonal)
        self.horizontal_button = horizontal_button

        builder.connect_signals(
            {
                "rectilinear-changed": (self._on_orthogonal_change,),
                "orientation-changed": (self._on_horizontal_change,),
            }
        )
        return builder.get_object("line-editor")

    @transactional
    def _on_orthogonal_change(self, button):
        if len(self.item.handles()) < 3:
            line_segment = Segment(self.item, None)
            line_segment.split_segment(0)
        active = button.get_active()
        self.item.orthogonal = active
        self.item.canvas.update_now()
        self.horizontal_button.set_sensitive(active)

    @transactional
    def _on_horizontal_change(self, button):
        self.item.horizontal = button.get_active()
        self.item.canvas.update_now()
