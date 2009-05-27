"""
State items property pages.

To register property pages implemented in this module, it is imported in
gaphor.adapter package.
"""

import gtk

from gaphor.core import _, inject, transactional
from gaphor import UML
from gaphor.diagram import items
from zope import interface, component
from gaphor.adapters.propertypages import NamedItemPropertyPage

class TransitionPropertyPage(NamedItemPropertyPage):
    """
    Transition property page allows to edit guard specification.
    """
    element_factory = inject('element_factory')

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
        entry.set_text(subject.guard and subject.guard.value or '')
        entry.connect('changed', self._on_guard_change)
        hbox.pack_start(entry)

        return page

    def update(self):
        pass

    @transactional
    def _on_guard_change(self, entry):
        value = entry.get_text().strip()
        subject = self.context.subject
        if subject.guard is None:
            subject.guard = self.element_factory.create(UML.Constraint)
            subject.guard.specification = self.element_factory.create(UML.LiteralSpecification)
        subject.guard.specification.value = value


component.provideAdapter(TransitionPropertyPage, name='Properties')

