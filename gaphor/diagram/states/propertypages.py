"""State items property pages.

To register property pages implemented in this module, it is imported in
gaphor.adapter package.
"""

from gi.repository import Gtk

from gaphor import UML
from gaphor.core import gettext, transactional
from gaphor.diagram.propertypages import (
    NamedItemPropertyPage,
    PropertyPageBase,
    PropertyPages,
    builder,
    create_hbox_label,
)
from gaphor.diagram.states.state import StateItem
from gaphor.diagram.states.transition import TransitionItem


@PropertyPages.register(UML.Transition)
class TransitionPropertyPage(PropertyPageBase):
    """Transition property page allows to edit guard specification."""

    name = "Transition"
    order = 15

    subject: UML.Transition

    def __init__(self, subject):
        self.subject = subject
        self.watcher = subject.watcher()
        self.builder = builder("transition-editor")

    def construct(self):
        subject = self.subject
        if not subject:
            return

        page = self.builder.get_object("transition-editor")

        guard = self.builder.get_object("guard")
        v = subject.guard.specification if subject.guard else ""
        guard.set_text(v)

        def handler(event):
            if event.element is subject.guard:
                guard.set_text(event.new_value or "")

        self.watcher.watch("guard[Constraint].specification", handler).subscribe_all()

        self.builder.connect_signals(
            {
                "guard-changed": (self._on_guard_change,),
                "transition-editor-destroy": (self.watcher.unsubscribe_all,),
            }
        )
        return page

    @transactional
    def _on_guard_change(self, entry):
        value = entry.get_text().strip()
        if not self.subject.guard:
            self.subject.guard = self.subject.model.create(UML.Constraint)
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

        hbox = create_hbox_label(self, page, gettext("Entry"))
        entry = Gtk.Entry()
        if subject.entry:
            entry.set_text(subject.entry.name or "")
        entry.connect("changed", self.on_text_change, self.set_entry)
        hbox.pack_start(entry, True, True, 0)

        hbox = create_hbox_label(self, page, gettext("Exit"))
        entry = Gtk.Entry()
        if subject.exit:
            entry.set_text(subject.exit.name or "")
        entry.connect("changed", self.on_text_change, self.set_exit)
        hbox.pack_start(entry, True, True, 0)

        hbox = create_hbox_label(self, page, gettext("Do Activity"))
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
