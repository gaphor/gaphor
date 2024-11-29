import math

from gi.repository import Gio

from gaphor import UML
from gaphor.diagram.propertypages import (
    LabelValue,
    PropertyPageBase,
    PropertyPages,
    handler_blocking,
    new_resource_builder,
    unsubscribe_all_on_destroy,
)
from gaphor.transaction import Transaction
from gaphor.UML.actions.activitynodes import DecisionNodeItem, ForkNodeItem
from gaphor.UML.actions.objectnode import ObjectNodeItem

new_builder = new_resource_builder("gaphor.UML.actions")


@PropertyPages.register(UML.ObjectNode)
class ObjectNodePropertyPage(PropertyPageBase):
    order = 15

    ORDERING_VALUES = ["unordered", "ordered", "LIFO", "FIFO"]

    def __init__(self, subject: UML.ObjectNode, event_manager):
        self.subject = subject
        self.event_manager = event_manager

    def construct(self):
        subject = self.subject

        if not subject or isinstance(subject, UML.ActivityParameterNode):
            return

        builder = new_builder(
            "object-node-editor",
            signals={
                "upper-bound-changed": (self._on_upper_bound_change,),
                "ordering-changed": (self._on_ordering_change,),
            },
        )

        upper_bound = builder.get_object("upper-bound")
        upper_bound.set_text(subject.upperBound or "")

        ordering = builder.get_object("ordering")
        ordering.set_selected(self.ORDERING_VALUES.index(subject.ordering))

        return builder.get_object("object-node-editor")

    def _on_upper_bound_change(self, entry):
        value = entry.get_text().strip()
        with Transaction(self.event_manager):
            self.subject.upperBound = value

    def _on_ordering_change(self, dropdown, _pspec):
        value = self.ORDERING_VALUES[dropdown.get_selected()]
        with Transaction(self.event_manager):
            self.subject.ordering = value


@PropertyPages.register(ObjectNodeItem)
class ShowObjectNodePropertyPage(PropertyPageBase):
    order = 16

    def __init__(self, item: ObjectNodeItem, event_manager):
        self.item = item
        self.event_manager = event_manager

    def construct(self):
        subject = self.item.subject

        if not subject:
            return

        builder = new_builder(
            "show-object-node-editor",
            signals={
                "show-ordering-changed": (self._on_ordering_show_change,),
            },
        )

        show_ordering = builder.get_object("show-ordering")
        show_ordering.set_active(self.item.show_ordering)

        return builder.get_object("show-object-node-editor")

    def _on_ordering_show_change(self, button, gparam):
        with Transaction(self.event_manager):
            self.item.show_ordering = button.get_active()


@PropertyPages.register(UML.ValueSpecificationAction)
class ValueSpecificationActionPropertyPage(PropertyPageBase):
    order = 15

    def __init__(self, item, event_manager):
        self.subject = item
        self.event_manager = event_manager

    def construct(self):
        builder = new_builder("value-specifiation-action-editor")

        value = builder.get_object("value")
        value.set_text(self.subject.value or "")
        value.connect("changed", self._on_value_change)

        return builder.get_object("value-specifiation-action-editor")

    def _on_value_change(self, entry):
        with Transaction(self.event_manager):
            value = entry.get_text()
            self.subject.value = value


@PropertyPages.register(UML.CallBehaviorAction)
class CallBehaviorActionPropertyPage(PropertyPageBase):
    order = 15

    def __init__(self, item, event_manager):
        self.subject = item
        self.event_manager = event_manager

    def construct(self):
        builder = new_builder("call-action-editor")

        dropdown = builder.get_object("behavior")
        options = self._behavior_options()
        dropdown.set_model(options)

        if self.subject.behavior:
            dropdown.set_selected(
                next(
                    n
                    for n, lv in enumerate(options)
                    if lv.value == self.subject.behavior.id
                )
            )

        dropdown.connect("notify::selected", self._on_behavior_changed)

        return builder.get_object("call-action-editor")

    def _behavior_options(self):
        options = Gio.ListStore.new(LabelValue)
        options.append(LabelValue("", None))

        for c in sorted(
            (c for c in self.subject.model.select(UML.Behavior) if c.name),
            key=lambda c: c.name or "",
        ):
            options.append(LabelValue(c.name, c.id))

        return options

    def _on_behavior_changed(self, dropdown, _pspec):
        with Transaction(self.event_manager):
            if id := dropdown.get_selected_item().value:
                element = self.subject.model.lookup(id)
                assert isinstance(element, UML.Behavior)
                self.subject.behavior = element
            else:
                del self.subject.behavior


@PropertyPages.register(DecisionNodeItem)
class DecisionNodePropertyPage(PropertyPageBase):
    order = 20

    def __init__(self, item, event_manager):
        self.item = item
        self.event_manager = event_manager

    def construct(self):
        builder = new_builder(
            "decision-node-editor",
            signals={"show-type-changed": (self._on_show_type_change,)},
        )

        show_type = builder.get_object("show-type")
        show_type.set_active(self.item.show_underlying_type)

        return builder.get_object("decision-node-editor")

    def _on_show_type_change(self, button, gparam):
        with Transaction(self.event_manager):
            self.item.show_underlying_type = button.get_active()


@PropertyPages.register(ForkNodeItem)
class ForkNodePropertyPage(PropertyPageBase):
    order = 20

    def __init__(self, item, event_manager):
        self.item = item
        self.event_manager = event_manager

    def construct(self):
        builder = new_builder(
            "fork-node-editor",
            signals={"horizontal-changed": (self._on_horizontal_change,)},
        )

        horizontal = builder.get_object("horizontal")
        horizontal.set_active(self.is_horizontal())

        return builder.get_object("fork-node-editor")

    def is_horizontal(self):
        return self.item.matrix[2] != 0

    def _on_horizontal_change(self, button, gparam):
        active = button.get_active()
        horizontal = self.is_horizontal()
        with Transaction(self.event_manager):
            if active and not horizontal:
                self.item.matrix.rotate(math.pi / 2)
            elif not active and horizontal:
                self.item.matrix.rotate(-math.pi / 2)
            self.item.request_update()


@PropertyPages.register(UML.JoinNode)
class JoinNodePropertyPage(PropertyPageBase):
    order = 15

    subject: UML.JoinNode

    def __init__(self, subject, event_manager):
        self.subject = subject
        self.event_manager = event_manager

    def construct(self):
        subject = self.subject

        if not subject:
            return

        builder = new_builder(
            "join-node-editor",
            signals={"join-spec-changed": (self._on_join_spec_change,)},
        )

        join_spec = builder.get_object("join-spec")
        join_spec.set_text(subject.joinSpec or "")

        return builder.get_object("join-node-editor")

    def _on_join_spec_change(self, entry):
        value = entry.get_text().strip()
        with Transaction(self.event_manager):
            self.subject.joinSpec = value


@PropertyPages.register(UML.ControlFlow)
@PropertyPages.register(UML.ObjectFlow)
class FlowPropertyPageAbstract(PropertyPageBase):
    """Flow item element editor."""

    order = 15

    subject: UML.ActivityEdge

    def __init__(self, subject, event_manager):
        self.subject = subject
        self.event_manager = event_manager
        self.watcher = subject and subject.watcher()

    def construct(self):
        subject = self.subject

        if not subject:
            return

        builder = new_builder(
            "transition-editor",
        )

        guard = builder.get_object("guard")
        guard.set_text(subject.guard or "")

        @handler_blocking(guard, "changed", self._on_guard_change)
        def handler(event):
            v = event.new_value
            if v != guard.get_text():
                guard.set_text(v or "")

        self.watcher.watch("guard", handler)

        return unsubscribe_all_on_destroy(
            builder.get_object("transition-editor"), self.watcher
        )

    def _on_guard_change(self, entry):
        value = entry.get_text().strip()
        with Transaction(self.event_manager):
            self.subject.guard = value


@PropertyPages.register(UML.Pin)
class PinPropertyPage(PropertyPageBase):
    """Pin element editor."""

    order = 15

    subject: UML.Pin

    def __init__(self, subject, event_manager):
        self.subject = subject
        self.event_manager = event_manager
        self.watcher = subject and subject.watcher()

    def construct(self):
        subject = self.subject

        if not subject:
            return

        builder = new_builder(
            "pin-editor",
            signals={
                "multiplicity-lower-changed": (self._on_multiplicity_lower_change,),
                "multiplicity-upper-changed": (self._on_multiplicity_upper_change,),
            },
        )

        dropdown = builder.get_object("type")
        model = self.list_of_classifiers(subject.model)
        dropdown.set_model(model)

        if subject.type:
            dropdown.set_selected(
                next(n for n, lv in enumerate(model) if lv.value == subject.type.id)
            )

        dropdown.connect("notify::selected", self._on_type_changed)

        multiplicity_lower = builder.get_object("multiplicity-lower")
        multiplicity_lower.set_text(subject.lowerValue or "")

        multiplicity_upper = builder.get_object("multiplicity-upper")
        multiplicity_upper.set_text(subject.upperValue or "")

        return builder.get_object("pin-editor")

    def list_of_classifiers(self, element_factory):
        options = Gio.ListStore.new(LabelValue)
        options.append(LabelValue("", None))

        for c in sorted(
            (c for c in element_factory.select(UML.Classifier) if c.name),
            key=lambda c: c.name or "",
        ):
            options.append(LabelValue(c.name, c.id))

        return options

    def _on_type_changed(self, dropdown, _pspec):
        subject = self.subject
        with Transaction(self.event_manager):
            if id := dropdown.get_selected_item().value:
                element = subject.model.lookup(id)
                assert isinstance(element, UML.Type)
                subject.type = element
            else:
                del subject.type

    def _on_multiplicity_lower_change(self, entry):
        value = entry.get_text().strip()
        with Transaction(self.event_manager):
            self.subject.lowerValue = value

    def _on_multiplicity_upper_change(self, entry):
        value = entry.get_text().strip()
        with Transaction(self.event_manager):
            self.subject.upperValue = value
