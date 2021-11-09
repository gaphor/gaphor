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

        model = self.subject.model

        builder = new_builder(
            "information-flow-editor",
            signals={
                "information-flow-changed": (self._on_information_flow_changed,),
                "information-flow-combo-changed": (
                    self._on_information_flow_name_changed,
                ),
                "invert-direction-changed": (self._invert_direction_changed,),
            },
        )

        self.combo = combo = builder.get_object("information-flow-combo")
        use_flow: Gtk.Switch = builder.get_object("use-information-flow")

        for c in model.select(UML.Class):
            combo.append(c.id, c.name)

        completion = Gtk.EntryCompletion()
        completion.set_model(combo.get_model())
        completion.set_minimum_key_length(1)
        completion.set_text_column(0)

        entry = combo.get_child()
        entry.set_completion(completion)

        use_flow.set_active(self.subject.informationFlow)
        self.combo.set_sensitive(use_flow.get_active())
        if self.subject.informationFlow and any(
            self.subject.informationFlow[:].conveyed
        ):
            entry.set_text(self.subject.informationFlow[0].conveyed[0].name or "")

        return builder.get_object("information-flow-editor")

    @transactional
    def _on_information_flow_changed(self, switch, gparam):
        active = switch.get_active()
        subject = self.subject
        if active and not subject.informationFlow:
            iflow = subject.model.create(UML.InformationFlow)
            subject.informationFlow = iflow
            iflow.informationSource = subject.end[0].role
            iflow.informationTarget = subject.end[1].role
        elif not active and self.subject.informationFlow:
            self.subject.informationFlow[0].unlink()
        self.combo.set_sensitive(switch.get_active())
        self.combo.get_child().set_text("")

    @transactional
    def _on_information_flow_name_changed(self, combo):
        if self.subject.informationFlow:
            model = self.subject.model
            iflow = self.subject.informationFlow[0]
            id = combo.get_active_id()
            if id:
                iitem = model.lookup(id)
                assert isinstance(iitem, UML.Classifier)
                iflow.conveyed = iitem

    @transactional
    def _invert_direction_changed(self, button):
        if self.subject.informationFlow:
            print("invert")
            iflow = self.subject.informationFlow[0]
            iflow.informationSource, iflow.informationTarget = (
                iflow.informationTarget,
                iflow.informationSource,
            )
