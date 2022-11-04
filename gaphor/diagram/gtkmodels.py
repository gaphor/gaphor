"""GTK-based types.

Thos module is normally imported in the method where it's used to avoid
the need for a global import of GTK.
"""

from gi.repository import Gtk

from gaphor.core import transactional


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

        self._indices: dict[tuple[str, str], int] = {}
        self._data = data

        # add labels to underlying model and store index information
        for i, (label, value) in enumerate(data):
            self.append([label])
            self._indices[value] = i

    def get_index(self, value):
        """Return index of a ``value``."""
        return self._indices[value]

    def get_value(self, index):
        """Get value for given ``index``."""
        return self._data[index][1]
