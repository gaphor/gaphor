from gi.repository import Gio

from gaphor import UML
from gaphor.diagram.propertypages import (
    LabelValue,
    PropertyPageBase,
    PropertyPages,
    new_resource_builder,
)
from gaphor.transaction import Transaction
from gaphor.UML.actions.partition import PartitionItem

new_builder = new_resource_builder("gaphor.UML.actions")


@PropertyPages.register(PartitionItem)
class PartitionPropertyPage(PropertyPageBase):
    """Partition property page."""

    order = 15

    def __init__(self, item: PartitionItem, event_manager):
        super().__init__()
        self.item = item
        self.event_manager = event_manager
        self.partitions = None

    def construct(self):
        """Creates the Partition Property Page."""
        builder = new_builder(
            "partition-editor",
            "num-partitions-adjustment",
            signals={"partitions-changed": (self._on_num_partitions_changed,)},
        )

        num_partitions = builder.get_object("num-partitions")
        num_partitions.set_value(len(self.item.partition))

        self.partitions = builder.get_object("partitions")
        if self.partitions:
            for partition in self.item.partition:
                self.partitions.append(self.construct_partition(partition))

        return builder.get_object("partition-editor")

    def construct_partition(self, partition):
        builder = new_builder(
            "partition",
            signals={
                "partition-name-changed": (self._on_partition_name_changed, partition),
            },
        )

        builder.get_object("partition-name").set_text(partition.name or "")

        dropdown = builder.get_object("partition-type")
        model = Gio.ListStore.new(LabelValue)
        model.append(LabelValue("", None))
        for c in sorted(
            (
                c
                for c in self.item.model.select(UML.Classifier)
                if c.name and not isinstance(c, UML.Behavior)
            ),
            key=lambda c: c.name or "",
        ):
            model.append(LabelValue(c.name, c.id))
        dropdown.set_model(model)

        if partition.represents:
            dropdown.set_selected(
                next(
                    n
                    for n, lv in enumerate(model)
                    if lv.value == partition.represents.id
                )
            )

        dropdown.connect("notify::selected", self._on_partition_type_changed, partition)

        return builder.get_object("partition")

    def _on_num_partitions_changed(self, spin_button):
        """Event handler for partition number spin button."""
        num_partitions = spin_button.get_value_as_int()
        with Transaction(self.event_manager):
            self.update_partitions(num_partitions)

    def _on_partition_name_changed(self, entry, partition):
        """Event handler for editing partition names."""
        with Transaction(self.event_manager):
            partition.name = entry.get_text()

    def _on_partition_type_changed(self, combo, _pspec, partition):
        """Event handler for editing partition names."""
        with Transaction(self.event_manager):
            if id := combo.get_selected_item().value:
                element = self.item.model.lookup(id)
                partition.represents = element
            else:
                del partition.represents

    def update_partitions(self, num_partitions) -> None:
        """Add and remove partitions.

        Clear the list store, then add or remove UML.ActivityPartitions
        to account for updates in the number of partitions, and finally
        rebuild the list store.
        """
        if not self.item.subject or not self.partitions:
            return

        while num_partitions > len(self.item.partition):
            partition = self.item.subject.model.create(UML.ActivityPartition)
            partition.name = self.item.diagram.gettext("New Swimlane")
            partition.activity = self.item.subject.activity
            self.item.partition.append(partition)

            self.partitions.append(self.construct_partition(partition))
        while num_partitions < len(self.item.partition):
            partition = self.item.partition[-1]
            partition.unlink()

            last_child = self.partitions.get_last_child()
            self.partitions.remove(last_child)

        diagram = self.item.diagram
        diagram.update(diagram.ownedPresentation)
