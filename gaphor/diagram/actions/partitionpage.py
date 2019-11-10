"""Activity partition property page."""

from gi.repository import Gtk

from gaphor.core import transactional, translate
from gaphor.diagram.actions.partition import PartitionItem
from gaphor.diagram.propertypages import NamedItemPropertyPage, PropertyPages


@PropertyPages.register(PartitionItem)
class PartitionPropertyPage(NamedItemPropertyPage):
    """Partition property page."""

    def construct(self):
        item = self.item

        page = super().construct()

        if item.subject:
            if not item._toplevel:
                hbox = Gtk.HBox(spacing=12)
                button = Gtk.CheckButton(translate("External"))
                button.set_active(item.subject.isExternal)
                button.connect("toggled", self._on_external_change)
                hbox.pack_start(button, True, True, 0)
                page.pack_start(hbox, False, True, 0)
            else:
                pass
                # hbox = Gtk.HBox(spacing=12)
                # button = Gtk.CheckButton(_('Dimension'))
                # button.set_active(item.subject.isDimension)
                # button.connect('toggled', self._on_dimension_change)

        return page

    @transactional
    def _on_external_change(self, button):
        item = self.item
        if item.subject:
            item.subject.isExternal = button.get_active()
        item.request_update()
