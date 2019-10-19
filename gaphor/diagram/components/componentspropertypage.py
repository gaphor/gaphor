from gi.repository import Gtk

from gaphor import UML
from gaphor.core import _, transactional
from gaphor.diagram.propertypages import PropertyPages, NamedItemPropertyPage
from gaphor.diagram.components import ComponentItem


@PropertyPages.register(ComponentItem)
class ComponentPropertyPage(NamedItemPropertyPage):
    """
    """

    subject: UML.Component

    def construct(self):
        page = super().construct()

        subject = self.subject

        if not subject:
            return page

        hbox = Gtk.HBox()
        page.pack_start(hbox, False, True, 0)

        button = Gtk.CheckButton(_("Indirectly instantiated"))
        button.set_active(subject.isIndirectlyInstantiated)
        button.connect("toggled", self._on_ii_change)
        hbox.pack_start(button, False, True, 0)

        return page

    @transactional
    def _on_ii_change(self, button):
        """
        Called when user clicks "Indirectly instantiated" check button.
        """
        subject = self.subject
        if subject:
            subject.isIndirectlyInstantiated = button.get_active()
