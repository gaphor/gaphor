from gi.repository import Gtk

from gaphor import UML
from gaphor.core import transactional
from gaphor.diagram.propertypages import PropertyPageBase, PropertyPages, builder


@PropertyPages.register(UML.Component)
class ComponentPropertyPage(PropertyPageBase):

    name = "Component"
    order = 15

    subject: UML.Component

    def __init__(self, subject):
        self.subject = subject
        self.builder = builder("component-editor")

    def construct(self):
        subject = self.subject

        if not subject:
            return

        ii = self.builder.get_object("indirectly-instantiated")
        ii.set_active(subject.isIndirectlyInstantiated)

        self.builder.connect_signals(
            {"indirectly-instantiated-changed": (self._on_ii_change,)}
        )
        return self.builder.get_object("component-editor")

    @transactional
    def _on_ii_change(self, button):
        """
        Called when user clicks "Indirectly instantiated" check button.
        """
        subject = self.subject
        if subject:
            subject.isIndirectlyInstantiated = button.get_active()
