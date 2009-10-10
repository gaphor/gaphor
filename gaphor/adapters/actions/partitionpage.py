"""
Activity partition property page.
"""
import gtk
from gaphor.core import _, inject, transactional
from gaphor.ui.interfaces import IPropertyPage
from gaphor.diagram import items
from zope import interface, component
from gaphor import UML


class PartitionPropertyPage(object):
    """
    Partition property page.
    """
    interface.implements(IPropertyPage)
    component.adapts(items.PartitionItem)

    element_factory = inject('element_factory')
    order = 0

    def __init__(self, context):
        self.context = context

    def construct(self):
        subject = self.context.subject
        page = gtk.VBox()

        hbox = gtk.HBox(spacing=12)
        button = gtk.CheckButton(_('Dimension'))
        hbox.pack_start(button)
        page.pack_start(hbox, expand=False)
        #button.set_active(self.context.show_stereotypes_attrs)
        #button.connect('toggled', self._on_show_stereotypes_attrs_change)

        hbox = gtk.HBox(spacing=12)
        button = gtk.CheckButton(_('External'))
        hbox.pack_start(button)
        page.pack_start(hbox, expand=False)
        page.show_all()

        return page


component.provideAdapter(PartitionPropertyPage, name='Properties')

# vim:sw=4:et:ai
