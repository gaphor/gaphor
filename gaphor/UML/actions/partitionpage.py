"""Activity partition property page."""

from gaphor import UML
from gaphor.core import gettext, transactional
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    new_resource_builder,
)
from gaphor.UML.actions.partition import PartitionItem

new_builder = new_resource_builder("gaphor.UML.actions")


@PropertyPages.register(PartitionItem)
class PartitionPropertyPage(PropertyPageBase):
    """Partition property page."""

    order = 15

    def __init__(self, item: PartitionItem):
        super().__init__()
        self.item = item

    def construct(self):
        """Creates the Partition Property Page."""
        builder = new_builder(
            "partition-editor",
            "num-partitions-adjustment",
            signals={"partitions-changed": (self._on_num_partitions_changed,)},
        )

        return builder.get_object("partition-editor")

    @transactional
    def _on_num_partitions_changed(self, spin_button):
        """Event handler for partition number spin button."""
        num_partitions = spin_button.get_value_as_int()
        self.update_partitions(num_partitions)

    @transactional
    def _on_partition_name_changed(self, widget, path, text):
        """Event handler for editing partition names."""
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
            partition.name = gettext("New Swimlane")
            partition.activity = self.item.subject.activity
            self.item.partition.append(partition)
        elif num_partitions < len(self.item.partition):
            partition = self.item.partition[-1]
            partition.unlink()
