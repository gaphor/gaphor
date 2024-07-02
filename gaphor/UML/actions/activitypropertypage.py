from __future__ import annotations

from gi.repository import Gio, GObject, Gtk

from gaphor import UML
from gaphor.core import event_handler, gettext
from gaphor.core.eventmanager import EventManager
from gaphor.core.format import format, parse
from gaphor.core.modeling import AssociationUpdated
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    handler_blocking,
    help_link,
    new_resource_builder,
    unsubscribe_all_on_destroy,
)
from gaphor.diagram.propertypages import (
    new_builder as diagram_new_builder,
)
from gaphor.transaction import Transaction
from gaphor.UML.actions.activity import ActivityParameterNodeItem
from gaphor.UML.propertypages import (
    ShowTypedElementPropertyPage,
    TypedElementPropertyPage,
    create_list_store,
    list_item_factory,
    list_view_activated,
    list_view_key_handler,
    text_field_handlers,
    update_list_store,
)

new_builder = new_resource_builder("gaphor.UML.actions")


class ActivityParameterNodeView(GObject.Object):
    def __init__(
        self,
        node: UML.ActivityParameterNode | None,
        activity: UML.Activity,
        event_manager: EventManager,
    ):
        super().__init__()
        self.node = node
        self.activity = activity
        self.event_manager = event_manager

    editing = GObject.Property(type=bool, default=False)

    @GObject.Property(type=str)
    def parameter(self) -> str:
        return (format(self.node.parameter) or " ") if self.node else ""

    @parameter.setter  # type: ignore[no-redef]
    def parameter(self, value):
        with Transaction(self.event_manager):
            if not self.node:
                if not value:
                    return

                model = self.activity.model
                node = model.create(UML.ActivityParameterNode)
                node.parameter = model.create(UML.Parameter)
                self.node = node
                self.activity.node = node
            parse(self.node.parameter, value)

    def empty(self):
        return not self.node

    def unlink(self):
        if self.node:
            with Transaction(self.event_manager):
                self.node.unlink()

    def swap(self, item1, item2):
        return self.activity.node.swap(item1.node, item2.node)


def activity_parameter_node_model(
    activity: UML.Activity, event_manager: EventManager
) -> Gio.ListModel:
    return create_list_store(
        ActivityParameterNodeView,
        (
            node
            for node in activity.node
            if isinstance(node, UML.ActivityParameterNode) and node.parameter
        ),
        lambda node: ActivityParameterNodeView(node, activity, event_manager),
    )


def update_activity_parameter_node_model(
    store: Gio.ListStore, activity: UML.Activity, event_manager: EventManager
) -> Gio.ListStore:
    return update_list_store(
        store,
        lambda item: item.node,
        (
            node
            for node in activity.node
            if isinstance(node, UML.ActivityParameterNode) and node.parameter
        ),
        lambda node: ActivityParameterNodeView(node, activity, event_manager),
    )


@PropertyPages.register(UML.Activity)
class ActivityPage(PropertyPageBase):
    order = 40

    def __init__(self, subject: UML.Activity, event_manager: EventManager):
        self.subject = subject
        self.event_manager = event_manager
        self.watcher = subject and subject.watcher()

    def construct(self):
        subject = self.subject

        if not subject:
            return

        builder = new_builder(
            "activity-editor",
            "parameters-info",
            signals={
                "parameter-activated": (list_view_activated,),
                "parameter-key-pressed": (list_view_key_handler,),
                "parameters-info-clicked": (self.on_parameters_info_clicked,),
            },
        )

        self.info = builder.get_object("parameters-info")
        help_link(builder, "parameters-info-icon", "parameters-info")

        column_view: Gtk.ListView = builder.get_object("parameter-list")

        for column, factory in zip(
            column_view.get_columns(),
            [
                list_item_factory(
                    "text-field-cell.ui",
                    klass=ActivityParameterNodeView,
                    attribute=ActivityParameterNodeView.parameter,
                    placeholder_text=gettext("New Parameter…"),
                    signal_handlers=text_field_handlers("parameter"),
                ),
            ],
        ):
            column.set_factory(factory)

        self.model = activity_parameter_node_model(subject, self.event_manager)
        selection = Gtk.SingleSelection.new(self.model)
        column_view.set_model(selection)

        if self.watcher:
            self.watcher.watch("node", self.on_nodes_changed)

        return unsubscribe_all_on_destroy(
            builder.get_object("activity-editor"), self.watcher
        )

    @event_handler(AssociationUpdated)
    def on_nodes_changed(self, event):
        update_activity_parameter_node_model(
            self.model, self.subject, self.event_manager
        )

    def on_parameters_info_clicked(self, image, event):
        self.info.set_visible(True)


@PropertyPages.register(UML.ActivityParameterNode)
class ActivityParameterNodeNamePropertyPage(PropertyPageBase):
    """An adapter which works for any named item view.

    It also sets up a table view which can be extended.
    """

    order = 10

    def __init__(self, subject: UML.ActivityParameterNode, event_manager: EventManager):
        super().__init__()
        self.subject = subject
        self.event_manager = event_manager
        self.watcher = subject.watcher() if subject else None

    def construct(self):
        if not self.subject:
            return

        assert self.watcher
        builder = diagram_new_builder(
            "name-editor",
        )

        subject = self.subject

        entry = builder.get_object("name-entry")
        entry.set_text(subject and subject.parameter and subject.parameter.name or "")

        @handler_blocking(entry, "changed", self._on_name_changed)
        def handler(event):
            if event.element is subject and event.new_value != entry.get_text():
                entry.set_text(event.new_value or "")

        self.watcher.watch("parameter.name", handler)

        return unsubscribe_all_on_destroy(
            builder.get_object("name-editor"), self.watcher
        )

    def _on_name_changed(self, entry):
        if self.subject.parameter.name != entry.get_text():
            with Transaction(self.event_manager):
                self.subject.parameter.name = entry.get_text()


@PropertyPages.register(UML.ActivityParameterNode)
class ActivityParameterNodeTypePropertyPage(TypedElementPropertyPage):
    @property
    def typed_element(self):
        return self.subject.parameter


@PropertyPages.register(ActivityParameterNodeItem)
class ShowActivityParameterNodeTypePropertyPage(ShowTypedElementPropertyPage):
    @property
    def typed_element(self):
        return self.item.subject.parameter


@PropertyPages.register(UML.ActivityParameterNode)
class ActivityParameterNodeDirectionPropertyPage(PropertyPageBase):
    DIRECTION = UML.Parameter.direction.values
    order = 40

    def __init__(self, subject: UML.ActivityParameterNode, event_manager):
        super().__init__()
        self.subject = subject
        self.event_manager = event_manager

    def construct(self):
        if not (self.subject and self.subject.parameter):
            return

        builder = new_builder(
            "parameter-direction-editor",
            signals={
                "parameter-direction-changed": (self._on_parameter_direction_changed,),
            },
        )

        direction = builder.get_object("parameter-direction")
        direction.set_selected(self.DIRECTION.index(self.subject.parameter.direction))

        return builder.get_object("parameter-direction-editor")

    def _on_parameter_direction_changed(self, dropdown, _pspec):
        with Transaction(self.event_manager):
            self.subject.parameter.direction = self.DIRECTION[dropdown.get_selected()]


@PropertyPages.register(ActivityParameterNodeItem)
class ShowActivityParameterNodeDirectionPropertyPage(PropertyPageBase):
    order = 40

    def __init__(self, item: ActivityParameterNodeItem, event_manager):
        super().__init__()
        self.item = item
        self.event_manager = event_manager

    def construct(self):
        if not (self.item.subject and self.item.subject.parameter):
            return

        builder = new_builder(
            "show-parameter-direction-editor",
            signals={
                "show-direction-changed": (self._on_show_direction_changed,),
            },
        )

        show_direction = builder.get_object("show-direction")
        show_direction.set_active(self.item.show_direction)

        return builder.get_object("show-parameter-direction-editor")

    def _on_show_direction_changed(self, button, _gspec):
        with Transaction(self.event_manager):
            self.item.show_direction = button.get_active()
