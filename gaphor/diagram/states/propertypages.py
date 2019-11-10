"""State items property pages.

To register property pages implemented in this module, it is imported in
gaphor.adapter package.
"""

from gi.repository import Gtk

from gaphor import UML
from gaphor.core import _, transactional
from gaphor.diagram.propertypages import (
    NamedItemPropertyPage,
    PropertyPages,
    create_hbox_label,
)
from gaphor.diagram.states.state import StateItem
from gaphor.diagram.states.transition import TransitionItem


@PropertyPages.register(TransitionItem)
class TransitionPropertyPage(NamedItemPropertyPage):
    """Transition property page allows to edit guard specification."""

    subject: UML.Transition

    def construct(self):
        page = super().construct()

        subject = self.subject

        if not subject:
            return page

        hbox = create_hbox_label(self, page, _("Guard"))
        entry = Gtk.Entry()
        v = subject.guard.specification
        entry.set_text(v if v else "")
        changed_id = entry.connect("changed", self._on_guard_change)
        hbox.pack_start(entry, True, True, 0)

        def handler(event):
            entry.handler_block(changed_id)
            v = event.new_value
            entry.set_text(v if v else "")
            entry.handler_unblock(changed_id)

        self.watcher.watch("guard[Constraint].specification", handler).subscribe_all()
        entry.connect("destroy", self.watcher.unsubscribe_all)

        return page

    @transactional
    def _on_guard_change(self, entry):
        value = entry.get_text().strip()
        self.subject.guard.specification = value


@PropertyPages.register(StateItem)
class StatePropertyPage(NamedItemPropertyPage):
    """State property page."""

    subject: UML.State

    def construct(self):
        page = super().construct()

        subject = self.subject

        if not subject:
            return page

        hbox = create_hbox_label(self, page, _("Entry"))
        entry = Gtk.Entry()
        if subject.entry:
            entry.set_text(subject.entry.name or "")
        entry.connect("changed", self.on_text_change, self.set_entry)
        hbox.pack_start(entry, True, True, 0)

        hbox = create_hbox_label(self, page, _("Exit"))
        entry = Gtk.Entry()
        if subject.exit:
            entry.set_text(subject.exit.name or "")
        entry.connect("changed", self.on_text_change, self.set_exit)
        hbox.pack_start(entry, True, True, 0)

        hbox = create_hbox_label(self, page, _("Do Activity"))
        entry = Gtk.Entry()
        if subject.doActivity:
            entry.set_text(self.subject.doActivity.name or "")
        entry.connect("changed", self.on_text_change, self.set_do_activity)
        hbox.pack_start(entry, True, True, 0)

        page.show_all()

        return page

    @transactional
    def on_text_change(self, entry, method):
        value = entry.get_text().strip()
        method(value)

    def set_entry(self, text):
        if not self.subject.entry:
            self.subject.entry = self.subject.model.create(UML.Activity)
        self.subject.entry.name = text

    def set_exit(self, text):
        if not self.subject.exit:
            self.subject.exit = self.subject.model.create(UML.Activity)
        self.subject.exit.name = text

    def set_do_activity(self, text):
        if not self.subject.doActivity:
            self.subject.doActivity = self.subject.model.create(UML.Activity)
        self.subject.doActivity.name = text
