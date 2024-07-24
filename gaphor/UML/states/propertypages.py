"""State items property pages.

To register property pages implemented in this module, it is imported in
gaphor.adapter package.
"""

from __future__ import annotations

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
from gaphor.UML.states.state import StateItem
from gaphor.UML.states.statemachine import StateMachineItem

new_builder = new_resource_builder("gaphor.UML.states")


@PropertyPages.register(UML.Transition)
class TransitionPropertyPage(PropertyPageBase):
    """Transition property page allows to edit trigger, guard, and action specification."""

    order = 15

    subject: UML.Transition

    def __init__(self, subject, event_manager):
        self.subject = subject
        self.event_manager = event_manager
        self.watcher = subject.watcher()

    def construct(self):
        subject = self.subject
        if not subject:
            return

        builder = new_builder("transition-editor")

        guard = builder.get_object("guard")
        if subject.guard:
            guard.set_text(subject.guard.specification or "")

        @handler_blocking(guard, "changed", self._on_guard_change)
        def guard_handler(event):
            if event.element is subject.guard and guard.get_text() != event.new_value:
                guard.set_text(event.new_value or "")

        self.watcher.watch("guard[Constraint].specification", guard_handler)

        trigger = builder.get_object("trigger")
        if subject.trigger:
            trigger.set_text(subject.trigger.name or "")

        @handler_blocking(trigger, "changed", self._on_trigger_change)
        def trigger_handler(event):
            if (
                event.element is subject.trigger
                and trigger.get_text() != event.new_value
            ):
                trigger.set_text(event.new_value or "")

        self.watcher.watch("trigger[Behavior].name", trigger_handler)

        action = builder.get_object("action")
        if subject.action:
            action.set_text(subject.action.name or "")

        @handler_blocking(action, "changed", self._on_action_change)
        def action_handler(event):
            if event.element is subject.action and action.get_text() != event.new_value:
                action.set_text(event.new_value or "")

        self.watcher.watch("action[Behavior].name", action_handler)

        return unsubscribe_all_on_destroy(
            builder.get_object("transition-editor"), self.watcher
        )

    def _on_guard_change(self, entry):
        value = entry.get_text().strip()
        with Transaction(self.event_manager):
            if not self.subject.guard:
                self.subject.guard = self.subject.model.create(UML.Constraint)
            self.subject.guard.specification = value

    def _on_trigger_change(self, entry):
        value = entry.get_text().strip()
        with Transaction(self.event_manager):
            if not self.subject.trigger:
                self.subject.trigger = self.subject.model.create(UML.Behavior)
            self.subject.trigger.name = value

    def _on_action_change(self, entry):
        value = entry.get_text().strip()
        with Transaction(self.event_manager):
            if not self.subject.action:
                self.subject.action = self.subject.model.create(UML.Behavior)
            self.subject.action.name = value


@PropertyPages.register(UML.State)
class StatePropertyPage(PropertyPageBase):
    """State property page."""

    order = 15
    subject: UML.State

    def __init__(self, subject, event_manager):
        self.subject = subject
        self.event_manager = event_manager

    def construct(self):
        subject = self.subject
        if not subject:
            return

        builder = new_builder("state-editor")
        options = self._behavior_options()

        entry_dropdown = builder.get_object("entry")
        entry_dropdown.set_model(options)

        if self.subject.entry:
            entry_dropdown.set_selected(
                next(
                    n
                    for n, lv in enumerate(options)
                    if lv.value == self.subject.entry.id
                )
            )

        entry_dropdown.connect("notify::selected", self._on_entry_behavior_changed)

        exit_dropdown = builder.get_object("exit")
        exit_dropdown.set_model(options)

        if self.subject.exit:
            exit_dropdown.set_selected(
                next(
                    n
                    for n, lv in enumerate(options)
                    if lv.value == self.subject.exit.id
                )
            )

        exit_dropdown.connect("notify::selected", self._on_exit_behavior_changed)

        do_activity_dropdown = builder.get_object("do-activity")
        do_activity_dropdown.set_model(options)

        if self.subject.doActivity:
            do_activity_dropdown.set_selected(
                next(
                    n
                    for n, lv in enumerate(options)
                    if lv.value == self.subject.doActivity.id
                )
            )

        do_activity_dropdown.connect(
            "notify::selected", self._on_do_activity_behavior_changed
        )

        return builder.get_object("state-editor")

    def _behavior_options(self):
        options = Gio.ListStore.new(LabelValue)
        options.append(LabelValue("", None))

        for c in sorted(
            (c for c in self.subject.model.select(UML.Behavior) if c.name),
            key=lambda c: c.name or "",
        ):
            options.append(LabelValue(c.name, c.id))

        return options

    def _on_entry_behavior_changed(self, dropdown, _pspec):
        with Transaction(self.event_manager):
            if id := dropdown.get_selected_item().value:
                element = self.subject.model.lookup(id)
                assert isinstance(element, UML.Behavior)
                self.subject.entry = element
            else:
                del self.subject.entry

    def _on_exit_behavior_changed(self, dropdown, _pspec):
        with Transaction(self.event_manager):
            if id := dropdown.get_selected_item().value:
                element = self.subject.model.lookup(id)
                assert isinstance(element, UML.Behavior)
                self.subject.exit = element
            else:
                del self.subject.exit

    def _on_do_activity_behavior_changed(self, dropdown, _pspec):
        with Transaction(self.event_manager):
            if id := dropdown.get_selected_item().value:
                element = self.subject.model.lookup(id)
                assert isinstance(element, UML.Behavior)
                self.subject.doActivity = element
            else:
                del self.subject.doActivity


@PropertyPages.register(StateItem)
@PropertyPages.register(StateMachineItem)
class RegionPropertyPage(PropertyPageBase):
    order = 15

    def __init__(self, item: StateItem | StateMachineItem, event_manager):
        super().__init__()
        self.item = item
        self.event_manager = event_manager

    def construct(self):
        if not self.item.subject:
            return

        builder = new_builder(
            "region-editor",
            "num-regions-adjustment",
            signals={
                "show-regions-changed": (self._on_show_regions_changed,),
                "regions-changed": (self._on_num_regions_changed,),
            },
        )

        num_regions = builder.get_object("num-regions")
        num_regions.set_value(len(self.item.subject.region))

        show_regions = builder.get_object("show-regions")
        show_regions.set_active(self.item.show_regions)

        return builder.get_object("region-editor")

    def _on_num_regions_changed(self, spin_button):
        num_regions = spin_button.get_value_as_int()
        with Transaction(self.event_manager):
            self.update_regions(num_regions)

    def _on_show_regions_changed(self, button, gparam):
        with Transaction(self.event_manager):
            self.item.show_regions = button.get_active()

    def update_regions(self, num_regions) -> None:
        if not self.item.subject:
            return

        while num_regions > len(self.item.subject.region):
            region = self.item.subject.model.create(UML.Region)
            self.item.subject.region = region

        while num_regions < len(self.item.subject.region):
            region = self.item.subject.region[-1]
            region.unlink()
