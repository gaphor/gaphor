"""Activity partition property page."""

from gi.repository import Gtk

from gaphor.core import gettext, transactional
from gaphor.diagram.actions.partition import PartitionItem
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages, new_builder


@PropertyPages.register(PartitionItem)
class PartitionPropertyPage(PropertyPageBase):
    """Partition property page."""

    order = 15

    def __init__(self, item):
        self.item = item

    def construct(self):
        item = self.item

        if item.toplevel:
            return

        builder = new_builder("partition-editor")

        external = builder.get_object("external")
        external.set_active(item.subject.isExternal)

        builder.connect_signals({"external-changed": (self._on_external_change,)})

        return builder.get_object("partition-editor")

    @transactional
    def _on_external_change(self, button):
        item = self.item
        if item.subject:
            item.subject.isExternal = button.get_active()
        item.request_update()
