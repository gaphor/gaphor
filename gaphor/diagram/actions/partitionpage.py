"""Activity partition property page."""

from gi.repository import Gtk

from gaphor import UML

from gaphor.core import _, inject, transactional
from gaphor.diagram.propertypages import PropertyPages, NamedItemPropertyPage
from gaphor.diagram.actions.partition import PartitionItem


@PropertyPages.register(PartitionItem)
class PartitionPropertyPage(NamedItemPropertyPage):
    """Partition property page."""

    element_factory = inject("element_factory")

    def construct(self):
        item = self.item

        page = super(PartitionPropertyPage, self).construct()

        if item.subject:
            if not item._toplevel:
                hbox = Gtk.HBox(spacing=12)
                button = Gtk.CheckButton(_("External"))
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
