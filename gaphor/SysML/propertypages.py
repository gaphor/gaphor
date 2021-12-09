from gaphor import UML
from gaphor.core import transactional
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    new_resource_builder,
)
from gaphor.SysML import sysml
from gaphor.SysML.blocks.block import BlockItem
from gaphor.SysML.requirements.requirement import RequirementItem
from gaphor.UML.classes.classespropertypages import AttributesPage, OperationsPage

new_builder = new_resource_builder("gaphor.SysML")


@PropertyPages.register(sysml.Requirement)
class RequirementPropertyPage(PropertyPageBase):

    order = 15

    def __init__(self, subject: sysml.Requirement):
        super().__init__()
        assert subject
        self.subject = subject
        self.watcher = subject.watcher()

    def construct(self):
        builder = new_builder(
            "requirement-editor",
            "requirement-text-buffer",
            signals={
                "requirement-id-changed": (self._on_id_changed,),
                "requirement-destroyed": (self.watcher.unsubscribe_all,),
            },
        )
        subject = self.subject

        entry = builder.get_object("requirement-id")
        entry.set_text(subject.externalId or "")

        text_view = builder.get_object("requirement-text")

        buffer = builder.get_object("requirement-text-buffer")
        if subject.text:
            buffer.set_text(subject.text)

        changed_id = buffer.connect("changed", self._on_text_changed)

        def text_handler(event):
            if not text_view.props.has_focus:
                buffer.handler_block(changed_id)
                buffer.set_text(event.new_value)
                buffer.handler_unblock(changed_id)

        self.watcher.watch("text", text_handler)

        return builder.get_object("requirement-editor")

    @transactional
    def _on_id_changed(self, entry):
        self.subject.externalId = entry.get_text()

    @transactional
    def _on_text_changed(self, buffer):
        self.subject.text = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), False
        )


PropertyPages.register(RequirementItem)(AttributesPage)
PropertyPages.register(RequirementItem)(OperationsPage)


@PropertyPages.register(BlockItem)
class PartsAndReferencesPage(PropertyPageBase):
    """An editor for Block items."""

    order = 30

    def __init__(self, item):
        super().__init__()
        self.item = item
        self.watcher = item.subject and item.subject.watcher()

    def construct(self):
        if not self.item.subject:
            return

        builder = new_builder(
            "parts-and-references-editor",
            signals={
                "show-parts-changed": (self._on_show_parts_change,),
                "show-references-changed": (self._on_show_references_change,),
            },
        )

        show_parts = builder.get_object("show-parts")
        show_parts.set_active(self.item.show_parts)

        show_references = builder.get_object("show-references")
        show_references.set_active(self.item.show_references)

        return builder.get_object("parts-and-references-editor")

    @transactional
    def _on_show_parts_change(self, button, gparam):
        self.item.show_parts = button.get_active()
        self.item.request_update()

    @transactional
    def _on_show_references_change(self, button, gparam):
        self.item.show_references = button.get_active()
        self.item.request_update()


@PropertyPages.register(sysml.Property)
class PropertyPropertyPage(PropertyPageBase):
    """An editor for Properties (a.k.a.

    attributes).
    """

    order = 30

    AGGREGATION = ("none", "shared", "composite")

    def __init__(self, subject: sysml.Property):
        super().__init__()
        self.subject = subject

    def construct(self):
        if not self.subject:
            return

        builder = new_builder(
            "property-editor",
            signals={"aggregation-changed": (self._on_aggregation_change,)},
        )

        aggregation = builder.get_object("aggregation")
        aggregation.set_active(self.AGGREGATION.index(self.subject.aggregation))

        return builder.get_object("property-editor")

    @transactional
    def _on_aggregation_change(self, combo):
        self.subject.aggregation = self.AGGREGATION[combo.get_active()]


@PropertyPages.register(sysml.Connector)
class ItemFlowPropertyPage(PropertyPageBase):
    """Information Flow on Connectors."""

    order = 35

    def __init__(self, subject: sysml.Connector):
        super().__init__()
        self.subject = subject

    def construct(self):
        if not self.subject:
            return

        builder = new_builder(
            "item-flow-editor",
            signals={
                "item-flow-active": (self._on_item_flow_active,),
                "item-flow-changed": (self._on_item_flow_name_changed,),
                "invert-direction-changed": (self._invert_direction_changed,),
            },
        )

        use_flow = builder.get_object("use-item-flow")
        self.entry = builder.get_object("item-flow-entry")

        use_flow.set_active(self.subject.informationFlow)
        self.entry.set_sensitive(use_flow.get_active())
        if self.subject.informationFlow and any(
            self.subject.informationFlow[:].itemProperty
        ):
            iflow = self.subject.informationFlow[0]
            assert isinstance(iflow, sysml.ItemFlow)
            self.entry.set_text(UML.format(iflow.itemProperty))

        return builder.get_object("item-flow-editor")

    @transactional
    def _on_item_flow_active(self, switch, gparam):
        active = switch.get_active()
        subject = self.subject
        if active and not subject.informationFlow:
            iflow = subject.model.create(sysml.ItemFlow)
            subject.informationFlow = iflow
            iflow.informationSource = subject.end[0].role
            iflow.informationTarget = subject.end[1].role
            iflow.itemProperty = subject.model.create(sysml.Property)
        elif not active and self.subject.informationFlow:
            self.subject.informationFlow[0].unlink()
        self.entry.set_sensitive(switch.get_active())
        self.entry.set_text("")

    @transactional
    def _on_item_flow_name_changed(self, entry):
        if self.subject.informationFlow:
            iflow = self.subject.informationFlow[0]
            assert isinstance(iflow, sysml.ItemFlow)
            UML.parse(iflow.itemProperty, entry.get_text())

    @transactional
    def _invert_direction_changed(self, button):
        if self.subject.informationFlow:
            iflow = self.subject.informationFlow[0]
            iflow.informationSource, iflow.informationTarget = (
                iflow.informationTarget,
                iflow.informationSource,
            )
