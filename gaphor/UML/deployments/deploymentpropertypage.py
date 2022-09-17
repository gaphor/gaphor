from gi.repository import Gtk

from gaphor import UML
from gaphor.core import transactional
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    combo_box_text_auto_complete,
    new_resource_builder,
)

new_builder = new_resource_builder("gaphor.UML.deployments")


@PropertyPages.register(UML.Connector)
class InformationFlowPropertyPage(PropertyPageBase):
    """Information Flow on Connectors."""

    order = 30

    name_entry: Gtk.Entry

    def __init__(self, subject: UML.Connector):
        super().__init__()
        self.subject = subject

    def construct(self):
        if not (
            self.subject
            and self.subject.informationFlow
            and type(self.subject.informationFlow[0]) is UML.InformationFlow
        ):
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

        combo_box_text_auto_complete(
            combo, ((c.id, c.name) for c in model.select(UML.Class))
        )

        use_flow.set_active(
            self.subject.informationFlow
            and type(self.subject.informationFlow[0]) is UML.InformationFlow
        )
        self.combo.set_sensitive(use_flow.get_active())
        if self.subject.informationFlow and any(
            self.subject.informationFlow[:].conveyed
        ):
            combo.get_child().set_text(
                self.subject.informationFlow[0].conveyed[0].name or ""
            )

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
            if id := combo.get_active_id():
                iitem = model.lookup(id)
                assert isinstance(iitem, UML.Classifier)
                iflow.conveyed = iitem

    @transactional
    def _invert_direction_changed(self, button):
        if self.subject.informationFlow:
            iflow = self.subject.informationFlow[0]
            iflow.informationSource, iflow.informationTarget = (
                iflow.informationTarget,
                iflow.informationSource,
            )
