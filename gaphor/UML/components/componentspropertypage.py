from gi.repository import Gtk

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


@PropertyPages.register(UML.Connector)
class InformationFlowPropertyPage(PropertyPageBase):
    """Information Flow on Connectors."""

    order = 30

    name_entry: Gtk.Entry

    def __init__(self, subject: UML.Connector):
        super().__init__()
        self.subject = subject

    def construct(self):
        if not self.subject:
            return

        builder = new_builder(
            "information-flow-editor",
            signals={
                "information-flow-changed": (self._on_information_flow_changed,),
                "information-flow-name-changed": (
                    self._on_information_flow_name_changed,
                ),
            },
        )

        self.name_entry = builder.get_object("information-flow-name")
        use_flow: Gtk.Switch = builder.get_object("use-information-flow")

        self.name_entry.set_sensitive(use_flow.get_active())
        if self.subject.informationFlow:
            self.name_entry.set_text(self.subject.informationFlow[0].name or "")

        return builder.get_object("information-flow-editor")

    @transactional
    def _on_information_flow_changed(self, switch, gparam):
        active = switch.get_active()
        subject = self.subject
        if active and not subject.informationFlow:
            iflow = subject.model.create(UML.InformationFlow)
            subject.informationFlow = iflow
            iflow.name = self.name_entry.get_text()
            iflow.informationSource = subject.end[0].role
            iflow.informationTarget = subject.end[1].role
        elif not active and self.subject.informationFlow:
            self.subject.informationFlow[0].unlink()
        self.name_entry.set_sensitive(switch.get_active())

    @transactional
    def _on_information_flow_name_changed(self, entry):
        if self.subject.informationFlow:
            self.subject.informationFlow[0].name = entry.get_text()
