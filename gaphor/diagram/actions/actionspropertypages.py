import math
from gi.repository import Gtk

from gaphor import UML
from gaphor.core import _, transactional
from ..propertypages import (
    PropertyPages,
    NamedElementPropertyPage,
    NamedItemPropertyPage,
    create_hbox_label,
)
from . import ObjectNodeItem, ForkNodeItem


@PropertyPages.register(ObjectNodeItem)
class ObjectNodePropertyPage(NamedItemPropertyPage):
    """
    """

    ORDERING_VALUES = ["unordered", "ordered", "LIFO", "FIFO"]

    def construct(self):
        page = super(ObjectNodePropertyPage, self).construct()

        subject = self.subject

        if not subject:
            return page

        hbox = create_hbox_label(self, page, _("Upper bound"))
        entry = Gtk.Entry()
        entry.set_text(subject.upperBound or "")
        entry.connect("changed", self._on_upper_bound_change)
        hbox.pack_start(entry, True, True, 0)

        hbox = create_hbox_label(self, page, "")
        combo = Gtk.ComboBoxText()
        for v in self.ORDERING_VALUES:
            combo.append_text(v)
        combo.set_active(self.ORDERING_VALUES.index(subject.ordering))
        combo.connect("changed", self._on_ordering_change)
        hbox.pack_start(combo, False, True, 0)

        hbox = create_hbox_label(self, page, "")
        button = Gtk.CheckButton(_("Ordering"))
        button.set_active(self.item.show_ordering)
        button.connect("toggled", self._on_ordering_show_change)
        hbox.pack_start(button, False, True, 0)

        return page

    def update(self):
        pass

    @transactional
    def _on_upper_bound_change(self, entry):
        value = entry.get_text().strip()
        self.item.set_upper_bound(value)

    @transactional
    def _on_ordering_change(self, combo):
        value = self.ORDERING_VALUES[combo.get_active()]
        self.subject.ordering = value

    @transactional
    def _on_ordering_show_change(self, button):
        self.item.show_ordering = button.get_active()
        self.item.set_ordering(self.subject.ordering)


@PropertyPages.register(ForkNodeItem)
class JoinNodePropertyPage(NamedItemPropertyPage):
    """
    """

    def construct(self):
        page = super(JoinNodePropertyPage, self).construct()

        subject = self.subject

        if not subject:
            return page

        hbox = Gtk.HBox()
        page.pack_start(hbox, False, True, 0)

        if isinstance(subject, UML.JoinNode):
            hbox = create_hbox_label(self, page, _("Join specification"))
            entry = Gtk.Entry()
            entry.set_text(subject.joinSpec or "")
            entry.connect("changed", self._on_join_spec_change)
            hbox.pack_start(entry, True, True, 0)

        button = Gtk.CheckButton(_("Horizontal"))
        button.set_active(self.item.matrix[2] != 0)
        button.connect("toggled", self._on_horizontal_change)
        page.pack_start(button, False, True, 0)

        return page

    def update(self):
        pass

    @transactional
    def _on_join_spec_change(self, entry):
        value = entry.get_text().strip()
        self.subject.joinSpec = value

    def _on_horizontal_change(self, button):
        if button.get_active():
            self.item.matrix.rotate(math.pi / 2)
        else:
            self.item.matrix.rotate(-math.pi / 2)
        self.item.request_update()


class FlowPropertyPageAbstract(NamedElementPropertyPage):
    """Flow item element editor."""

    def construct(self):
        page = super(FlowPropertyPageAbstract, self).construct()

        subject = self.subject

        if not subject:
            return page

        hbox = create_hbox_label(self, page, _("Guard"))
        entry = Gtk.Entry()
        entry.set_text(subject.guard or "")
        changed_id = entry.connect("changed", self._on_guard_change)
        hbox.pack_start(entry, True, True, 0)

        def handler(event):
            entry.handler_block(changed_id)
            v = event.new_value
            entry.set_text(v if v else "")
            entry.handler_unblock(changed_id)

        self.watcher.watch("guard", handler).register_handlers()
        entry.connect("destroy", self.watcher.unregister_handlers)

        return page

    @transactional
    def _on_guard_change(self, entry):
        value = entry.get_text().strip()
        self.subject.guard = value


# TODO: unify ObjectFlowPropertyPage and ControlFlowPropertyPage
#   after introducing common class for element editors
@PropertyPages.register(UML.ControlFlow)
class ControlFlowPropertyPage(FlowPropertyPageAbstract):
    pass


@PropertyPages.register(UML.ObjectFlow)
class ObjectFlowPropertyPage(FlowPropertyPageAbstract):
    pass
