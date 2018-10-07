"""
Activity partition property page.
"""
from zope import component

from gi.repository import Gtk
from zope.interface import implementer

from gaphor import UML

from gaphor.adapters.propertypages import NamedItemPropertyPage
from gaphor.core import _, inject, transactional
from gaphor.diagram import items
from gaphor.ui.interfaces import IPropertyPage


@implementer(IPropertyPage)
class PartitionPropertyPage(NamedItemPropertyPage):
    """
    Partition property page.
    """

    component.adapts(items.PartitionItem)

    element_factory = inject('element_factory')

    def construct(self):
        item = self.item

        page = super(PartitionPropertyPage, self).construct()

        if item.subject:
            if not item._toplevel:
                hbox = Gtk.HBox(spacing=12)
                button = Gtk.CheckButton(_('External'))
                button.set_active(item.subject.isExternal)
                button.connect('toggled', self._on_external_change)
                hbox.pack_start(button, True, True, 0)
                page.pack_start(hbox, False, True, 0)
            else:
                pass
                #hbox = Gtk.HBox(spacing=12)
                #button = Gtk.CheckButton(_('Dimension'))
                #button.set_active(item.subject.isDimension)
                #button.connect('toggled', self._on_dimension_change)

        return page

    @transactional
    def _on_external_change(self, button):
        item = self.item
        if item.subject:
            item.subject.isExternal = button.get_active()
        item.request_update()


component.provideAdapter(PartitionPropertyPage, name='Properties')


# vim:sw=4:et:ai
