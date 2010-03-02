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
from gaphor.adapters.propertypages import NamedItemPropertyPage, create_hbox_label

class TransitionPropertyPage(NamedItemPropertyPage):
    """
    Transition property page allows to edit guard specification.
    """
    element_factory = inject('element_factory')

    component.adapts(items.TransitionItem)

    def construct(self):
        page = super(TransitionPropertyPage, self).construct()

        subject = self.subject

        if not subject:
            return page

        hbox = create_hbox_label(self, page, _('Guard'))
        entry = gtk.Entry()
        v = subject.guard.specification.value
        entry.set_text(v if v else '')
        entry.connect('changed', self._on_guard_change)
        changed_id = entry.connect('changed', self._on_guard_change)
        hbox.pack_start(entry)

        def handler(event):
            entry.handler_block(changed_id)
            v = event.new_value
            entry.set_text(v if v else '')
            entry.handler_unblock(changed_id)

        self.watcher.watch('guard<Constraint>.specification<LiteralSpecification>.value', handler).register_handlers()
        entry.connect('destroy', self.watcher.unregister_handlers)

        return page

    def update(self):
        pass

    @transactional
    def _on_guard_change(self, entry):
        value = entry.get_text().strip()
        self.subject.guard.specification.value = value


component.provideAdapter(TransitionPropertyPage, name='Properties')


class StatePropertyPage(NamedItemPropertyPage):
    """
    State property page.
    """
    element_factory = inject('element_factory')

    component.adapts(items.StateItem)

    def construct(self):
        page = super(StatePropertyPage, self).construct()

        subject = self.subject
 
        if not subject:
            return page

        hbox = create_hbox_label(self, page, _('Entry'))
        entry = gtk.Entry()
        if self.item._entry.subject:
            entry.set_text(self.item._entry.subject.name)
        entry.connect('changed', self._on_text_change, self.item.set_entry)
        hbox.pack_start(entry)

        hbox = create_hbox_label(self, page, _('Exit'))
        entry = gtk.Entry()
        if self.item._exit.subject:
            entry.set_text(self.item._exit.subject.name)
        entry.connect('changed', self._on_text_change, self.item.set_exit)
        hbox.pack_start(entry)

        hbox = create_hbox_label(self, page, _('Do Activity'))
        entry = gtk.Entry()
        if self.item._do_activity.subject:
            entry.set_text(self.item._do_activity.subject.name)
        entry.connect('changed', self._on_text_change, self.item.set_do_activity)
        hbox.pack_start(entry)

        page.show_all()

        return page

    def update(self):
        pass

    @transactional
    def _on_text_change(self, entry, method):
        value = entry.get_text().strip()
        method(value)



component.provideAdapter(StatePropertyPage, name='Properties')

