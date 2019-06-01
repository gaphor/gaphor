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
import gaphas.item
from gi.repository import GObject
from gi.repository import Gdk
from gi.repository import Gtk

from gaphor import UML
from gaphor.core import _, transactional


class _PropertyPages:
    """
    Generic handler for property pages.

    Property pages are collected on type.
    """

    def __init__(self):
        self.pages = []

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

    order = 0  # Order number, used for ordered display
    name = "Properties"

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
        super(EditableTreeModel, self).__init__(*cols)
        self._item = item

        for data in self._get_rows():
            self.append(data)
        self._add_empty()

    def refresh(self, obj):
        for row in self:
            if row[-1] is obj:
                self._set_object_value(row, len(row) - 1, obj)
                self.row_changed(row.path, row.iter)
                return

    def _get_rows(self):
        """Return rows to be edited.

        Last column has to contain object being edited.
        """

        raise NotImplemented

    def _create_object(self):
        """
        Create new object.
        """
        raise NotImplemented

    def _set_object_value(self, row, col, value):
        """
        Update row's column with a value.
        """
        raise NotImplemented

    def _swap_objects(self, o1, o2):
        """
        Swap two objects. If objects are swapped, then return ``True``.
        """
        raise NotImplemented

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
            super(EditableTreeModel, self).swap(a, b)

    def _add_empty(self):
        """
        Add empty row to the end of the model.
        """
        self.append([None] * self.get_n_columns())

    @transactional
    def set_value(self, iter, col, value):
        row = self[iter][:]

        if col == 0 and not value and row[-1]:
            # kill row and delete object if text of first column is empty
            self.remove(iter)

        elif col == 0 and value and not row[-1]:
            # create new object
            obj = self._create_object()
            row[-1] = obj
            self._set_object_value(row, col, value)
            self._add_empty()

        elif row[-1]:
            self._set_object_value(row, col, value)

        self.set(iter, list(range(len(row))), row)

        self.set(iter, list(range(len(row))), row)

    def remove(self, iter):
        """
        Remove object from GTK model and destroy it.
        """
        obj = self._get_object(iter)
        if obj:
            obj.unlink()
            # self._item.request_update(matrix=False)
            return super(EditableTreeModel, self).remove(iter)
        else:
            return iter


@transactional
def remove_on_keypress(tree, event):
    """Remove selected items from GTK model on ``backspace`` keypress."""

    k = Gdk.keyval_name(event.keyval).lower()
    if k == "backspace" or k == "kp_delete":
        model, iter = tree.get_selection().get_selected()
        if iter:
            model.remove(iter)


@transactional
def swap_on_keypress(tree, event):
    """Swap selected and previous (or next) items."""

    k = Gdk.keyval_name(event.keyval).lower()
    if k == "equal" or k == "kp_add":
        model, iter = tree.get_selection().get_selected()
        model.swap(iter, model.iter_next(iter))
        return True
    elif k == "minus":
        model, iter = tree.get_selection().get_selected()
        model.swap(iter, model.iter_previous(iter))
        return True


@transactional
def on_text_cell_edited(renderer, path, value, model, col=0):
    """Update editable tree model based on fresh user input."""

    iter = model.get_iter(path)
    model.set_value(iter, col, value)


@transactional
def on_bool_cell_edited(renderer, path, model, col):
    """Update editable tree model based on fresh user input."""

    iter = model.get_iter(path)
    model.set_value(iter, col, renderer.get_active())


class UMLComboModel(Gtk.ListStore):
    """UML combo box model.

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
        super(UMLComboModel, self).__init__(str)

        self._indices = {}
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


def create_uml_combo(data, callback):
    """
    Create a combo box using ``UMLComboModel`` model.

    Combo box is returned.
    """
    model = UMLComboModel(data)
    combo = Gtk.ComboBox(model=model)
    cell = Gtk.CellRendererText()
    combo.pack_start(cell, True)
    combo.add_attribute(cell, "text", 0)
    combo.connect("changed", callback)
    return combo


def create_hbox_label(adapter, page, label):
    """
    Create a HBox with a label for given property page adapter and page
    itself.
    """
    hbox = Gtk.HBox(spacing=12)
    label = Gtk.Label(label=label)
    # label.set_alignment(0.0, 0.5)
    adapter.size_group.add_widget(label)
    hbox.pack_start(label, False, True, 0)
    page.pack_start(hbox, False, True, 0)
    return hbox


def create_tree_view(model, names, tip="", ro_cols=None):
    """
    Create a tree view for an editable tree model.

    :Parameters:
     model
        Model, for which tree view is created.
     names
        Names of columns.
     tip
        User interface tool tip for tree view.
     ro_cols
        Collection of indices pointing read only columns.
    """
    if ro_cols is None:
        ro_cols = set()

    tree_view = Gtk.TreeView(model=model)

    n = model.get_n_columns() - 1
    for name, i in zip(names, list(range(n))):
        col_type = model.get_column_type(i)
        if col_type == GObject.TYPE_STRING:
            renderer = Gtk.CellRendererText()
            renderer.set_property("editable", i not in ro_cols)
            renderer.set_property("is-expanded", True)
            renderer.connect("edited", on_text_cell_edited, model, i)
            col = Gtk.TreeViewColumn(name, renderer, text=i)
            col.set_expand(True)
            tree_view.append_column(col)
        elif col_type == GObject.TYPE_BOOLEAN:
            renderer = Gtk.CellRendererToggle()
            renderer.set_property("activatable", i not in ro_cols)
            renderer.connect("toggled", on_bool_cell_edited, model, i)
            col = Gtk.TreeViewColumn(name, renderer, active=i)
            col.set_expand(False)
            tree_view.append_column(col)

    tree_view.connect("key_press_event", remove_on_keypress)
    tree_view.connect("key_press_event", swap_on_keypress)

    tip = (
        tip
        + """
Press ENTER to edit item, BS/DEL to remove item.
Use -/= to move items up or down.\
    """
    )
    tree_view.set_tooltip_text(tip)

    return tree_view


@PropertyPages.register(UML.NamedElement)
class NamedElementPropertyPage(PropertyPageBase):
    """An adapter which works for any named item view.

    It also sets up a table view which can be extended.
    """

    order = 10

    NAME_LABEL = _("Name")

    def __init__(self, subject):
        assert subject is None or isinstance(subject, UML.NamedElement), "%s" % type(
            subject
        )
        self.subject = subject
        self.watcher = subject.watcher()
        self.size_group = Gtk.SizeGroup.new(Gtk.SizeGroupMode.HORIZONTAL)

    def construct(self):
        page = Gtk.VBox()

        subject = self.subject
        if not subject:
            return page

        hbox = create_hbox_label(self, page, self.NAME_LABEL)
        entry = Gtk.Entry()
        entry.set_text(subject and subject.name or "")
        hbox.pack_start(entry, True, True, 0)
        page.default = entry

        # monitor subject.name attribute
        changed_id = entry.connect("changed", self._on_name_change)

        def handler(event):
            if event.element is subject and event.new_value is not None:
                entry.handler_block(changed_id)
                entry.set_text(event.new_value)
                entry.handler_unblock(changed_id)

        self.watcher.watch("name", handler).subscribe_all()
        entry.connect("destroy", self.watcher.unsubscribe_all)

        return page

    @transactional
    def _on_name_change(self, entry):
        self.subject.name = entry.get_text()


class NamedItemPropertyPage(NamedElementPropertyPage):
    """
    Base class for named _diagram item_ based adapters.
    """

    def __init__(self, item):
        self.item = item
        super().__init__(item.subject)


@PropertyPages.register(gaphas.item.Line)
class LineStylePage(PropertyPageBase):
    """Basic line style properties: color, orthogonal, etc."""

    order = 400
    name = "Style"

    def __init__(self, item):
        super(LineStylePage, self).__init__()
        self.item = item
        self.size_group = Gtk.SizeGroup(mode=Gtk.SizeGroupMode.HORIZONTAL)

    def construct(self):
        page = Gtk.VBox()

        hbox = Gtk.HBox()
        label = Gtk.Label(label="")
        label.set_justify(Gtk.Justification.LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, False, True, 0)

        button = Gtk.CheckButton(label=_("Orthogonal"))
        button.set_active(self.item.orthogonal)
        button.connect("toggled", self._on_orthogonal_change)
        hbox.pack_start(button, True, True, 0)

        page.pack_start(hbox, False, True, 0)

        if len(self.item.handles()) < 3:
            # Only one segment
            button.props.sensitive = False

        hbox = Gtk.HBox()
        label = Gtk.Label(label="")
        label.set_justify(Gtk.Justification.LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, False, True, 0)

        button = Gtk.CheckButton(label=_("Horizontal"))
        button.set_active(self.item.horizontal)
        button.connect("toggled", self._on_horizontal_change)
        hbox.pack_start(button, True, True, 0)

        page.pack_start(hbox, False, True, 0)

        return page

    @transactional
    def _on_orthogonal_change(self, button):
        self.item.orthogonal = button.get_active()

    @transactional
    def _on_horizontal_change(self, button):
        self.item.horizontal = button.get_active()
