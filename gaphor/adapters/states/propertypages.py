"""
State items property pages.

To register property pages implemented in this module, it is imported in
gaphor.adapter package.
"""

import gtk

from gaphor.core import _, transactional
from gaphor.diagram import items
from gaphor.ui.interfaces import IPropertyPage
from zope import interface, component
from gaphor.adapters.propertypages import NamedItemPropertyPage

class TransitionPropertyPage(NamedItemPropertyPage):
    """
    Transition property page allows to edit guard specification.
    """

    interface.implements(IPropertyPage)
    component.adapts(items.TransitionItem)

    def construct(self):
        page = super(TransitionPropertyPage, self).construct()

        subject = self.context.subject
        
        if not subject:
            return page

        hbox = gtk.HBox()
        page.pack_start(hbox, expand=False)

        label = gtk.Label(_('Guard'))
        label.set_justify(gtk.JUSTIFY_LEFT)
        self.size_group.add_widget(label)
        hbox.pack_start(label, expand=False)
        entry = gtk.Entry()        
        entry.set_text(subject.guard and subject.guard.constraint.value or '')
        entry.connect('changed', self._on_guard_change)
        hbox.pack_start(entry)

        return page

    def update(self):
        pass

    @transactional
    def _on_guard_change(self, entry):
        value = entry.get_text().strip()
        self.context.set_guard(value)


component.provideAdapter(TransitionPropertyPage, name='Properties')

