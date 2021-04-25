from gaphor import UML
from gaphor.core import transactional
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    new_resource_builder,
)

new_builder = new_resource_builder("gaphor.UML.components")


@PropertyPages.register(UML.Component)
class ComponentPropertyPage(PropertyPageBase):

    order = 15

    subject: UML.Component

    def __init__(self, subject):
        self.subject = subject

    def construct(self):
        subject = self.subject

        if not subject:
            return

        builder = new_builder(
            "component-editor",
            signals={"indirectly-instantiated-changed": (self._on_ii_change,)},
        )

        ii = builder.get_object("indirectly-instantiated")
        ii.set_active(subject.isIndirectlyInstantiated)

        return builder.get_object("component-editor")

    @transactional
    def _on_ii_change(self, button, gparam):
        """Called when user clicks "Indirectly instantiated" check button."""
        subject = self.subject
        if subject:
            subject.isIndirectlyInstantiated = button.get_active()
