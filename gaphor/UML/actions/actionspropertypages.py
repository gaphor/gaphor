import math

from gaphor import UML
from gaphor.core import transactional
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    new_resource_builder,
)
from gaphor.UML.actions.activitynodes import DecisionNodeItem, ForkNodeItem
from gaphor.UML.actions.objectnode import ObjectNodeItem

new_builder = new_resource_builder("gaphor.UML.actions")


@PropertyPages.register(ObjectNodeItem)
class ObjectNodePropertyPage(PropertyPageBase):

    order = 15

    ORDERING_VALUES = ["unordered", "ordered", "LIFO", "FIFO"]

    subject: UML.ObjectNode
    item: ObjectNodeItem

    def __init__(self, item):
        self.item = item

    def construct(self):
        subject = self.item.subject

        if not subject:
            return

        builder = new_builder(
            "object-node-editor",
            signals={
                "upper-bound-changed": (self._on_upper_bound_change,),
                "ordering-changed": (self._on_ordering_change,),
                "show-ordering-changed": (self._on_ordering_show_change,),
            },
        )

        upper_bound = builder.get_object("upper-bound")
        upper_bound.set_text(subject.upperBound or "")

        ordering = builder.get_object("ordering")
        ordering.set_active(self.ORDERING_VALUES.index(subject.ordering))

        show_ordering = builder.get_object("show-ordering")
        show_ordering.set_active(self.item.show_ordering)

        return builder.get_object("object-node-editor")

    @transactional
    def _on_upper_bound_change(self, entry):
        value = entry.get_text().strip()
        self.item.subject.upperBound = value

    @transactional
    def _on_ordering_change(self, combo):
        value = self.ORDERING_VALUES[combo.get_active()]
        self.item.subject.ordering = value

    @transactional
    def _on_ordering_show_change(self, button, gparam):
        self.item.show_ordering = button.get_active()


@PropertyPages.register(DecisionNodeItem)
class DecisionNodePropertyPage(PropertyPageBase):

    order = 20

    def __init__(self, item):
        self.item = item

    def construct(self):
        builder = new_builder(
            "decision-node-editor",
            signals={"show-type-changed": (self._on_show_type_change,)},
        )

        show_type = builder.get_object("show-type")
        show_type.set_active(self.item.show_underlaying_type)

        return builder.get_object("decision-node-editor")

    @transactional
    def _on_show_type_change(self, button, gparam):
        self.item.show_underlaying_type = button.get_active()


@PropertyPages.register(ForkNodeItem)
class ForkNodePropertyPage(PropertyPageBase):

    order = 20

    def __init__(self, item):
        self.item = item

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

    @transactional
    def _on_horizontal_change(self, button, gparam):
        active = button.get_active()
        horizontal = self.is_horizontal()
        if active and not horizontal:
            self.item.matrix.rotate(math.pi / 2)
        elif not active and horizontal:
            self.item.matrix.rotate(-math.pi / 2)
        self.item.request_update()


@PropertyPages.register(UML.JoinNode)
class JoinNodePropertyPage(PropertyPageBase):

    order = 15

    subject: UML.JoinNode

    def __init__(self, subject):
        self.subject = subject

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

    @transactional
    def _on_join_spec_change(self, entry):
        value = entry.get_text().strip()
        self.subject.joinSpec = value


@PropertyPages.register(UML.ControlFlow)
@PropertyPages.register(UML.ObjectFlow)
class FlowPropertyPageAbstract(PropertyPageBase):
    """Flow item element editor."""

    order = 15

    subject: UML.ActivityEdge

    def __init__(self, subject):
        self.subject = subject
        self.watcher = subject and subject.watcher()

    def construct(self):
        subject = self.subject

        if not subject:
            return

        builder = new_builder(
            "transition-editor",
            signals={
                "guard-changed": (self._on_guard_change,),
                "transition-destroy": (self.watcher.unsubscribe_all,),
            },
        )

        guard = builder.get_object("guard")
        guard.set_text(subject.guard or "")

        def handler(event):
            v = event.new_value
            if v != guard.get_text():
                guard.set_text(v or "")

        self.watcher.watch("guard", handler)

        return builder.get_object("transition-editor")

    @transactional
    def _on_guard_change(self, entry):
        value = entry.get_text().strip()
        self.subject.guard = value
