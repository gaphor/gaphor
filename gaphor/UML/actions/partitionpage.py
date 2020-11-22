"""Activity partition property page."""

from gi.repository import Gtk

from gaphor.core import transactional
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages, new_builder
from gaphor.UML.actions.partition import PartitionItem


@PropertyPages.register(PartitionItem)
class PartitionPropertyPage(PropertyPageBase):
    """Partition property page."""

    order = 15

    def __init__(self, item: PartitionItem):
        super().__init__()
        self.item = item
        self.watcher = item.watcher()
        self.liststore = Gtk.ListStore(int, str)

    def text_edited(self, widget, path, text):
        print("text edited")
        self.liststore[path][1] = text
        print(path)

    def construct(self):
        item = self.item
        builder = new_builder("partition-editor")

        num_partitions = builder.get_object("num-partitions")
        adjustment = Gtk.Adjustment(
            value=item.num_partitions,
            lower=2,
            upper=10,
            step_increment=1,
            page_increment=5,
        )
        num_partitions.set_adjustment(adjustment)
        builder.connect_signals({"partitions-changed": (self._on_partitions_changed,)})

        self.liststore.append([1, "Engine"])
        self.liststore.append([2, "Transmission"])
        self.liststore.append([3, "Wheel"])

        treeview = builder.get_object("partition-treeview")
        treeview.set_model(self.liststore)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn(title="#", cell_renderer=renderer_text, text=0)
        treeview.append_column(column_text)

        renderer_editabletext = Gtk.CellRendererText()
        renderer_editabletext.set_property("editable", True)

        column_editabletext = Gtk.TreeViewColumn(
            title="Name", cell_renderer=renderer_editabletext, text=1
        )
        treeview.append_column(column_editabletext)

        renderer_editabletext.connect("edited", self.text_edited)

        return builder.get_object("partition-editor")

    @transactional
    def _on_partitions_changed(self, spin_button):
        self.item.num_partitions = spin_button.get_value_as_int()
