"""Activity partition property page."""

from gi.repository import Gtk

from gaphor import UML
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
        self.list_store = Gtk.ListStore(int, str)

    def construct(self):
        """Creates the Partition Property Page."""
        builder = new_builder("partition-editor")

        num_partitions = builder.get_object("num-partitions")
        adjustment = Gtk.Adjustment(
            value=len(self.item.partition),
            lower=1,
            upper=10,
            step_increment=1,
            page_increment=5,
        )
        num_partitions.set_adjustment(adjustment)
        builder.connect_signals(
            {"partitions-changed": (self._on_num_partitions_changed,)}
        )

        treeview = builder.get_object("partition-treeview")
        treeview.set_model(self.list_store)

        renderer_text = Gtk.CellRendererText()
        column_text = Gtk.TreeViewColumn(title="#", cell_renderer=renderer_text, text=0)
        treeview.append_column(column_text)

        renderer_editable_text = Gtk.CellRendererText()
        renderer_editable_text.set_property("editable", True)

        column_editabletext = Gtk.TreeViewColumn(
            title="Name", cell_renderer=renderer_editable_text, text=1
        )
        treeview.append_column(column_editabletext)

        renderer_editable_text.connect("edited", self._on_partition_name_changed)

        self.update_list_store()

        return builder.get_object("partition-editor")

    @transactional
    def _on_num_partitions_changed(self, spin_button):
        """Event handler for partition number spin button."""
        num_partitions = spin_button.get_value_as_int()
        self.update_partitions(num_partitions)
        self.update_list_store()

    @transactional
    def _on_partition_name_changed(self, widget, path, text):
        """Event handler for editing partition names."""
        self.list_store[path][1] = text
        self.item.partition[int(path)].name = text

    def update_partitions(self, num_partitions) -> None:
        """Add and remove partitions.

        Clear the list store, then add or remove UML.ActivityPartitions
        to account for updates in the number of partitions, and finally
        rebuild the list store.
        """
        if not self.item.subject:
            return
        if num_partitions > len(self.item.partition):
            partition = self.item.subject.model.create(UML.ActivityPartition)
            partition.name = "NewActivityPartition"
            partition.activity = self.item.subject.activity
            self.item.partition.append(partition)
        elif num_partitions < len(self.item.partition):
            partition = self.item.partition[-1]
            partition.unlink()

    def update_list_store(self):
        self.list_store.clear()
        for num, partition in enumerate(self.item.partition, start=1):
            self.list_store.append([num, partition.name])
