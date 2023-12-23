from __future__ import annotations

from gi.repository import Gio, GLib, GObject, Gtk

from gaphor import UML
from gaphor.core import event_handler, transactional
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
from gaphor.i18n import translated_ui_string
from gaphor.UML.actions.activity import ActivityItem
from gaphor.UML.propertypages import (
    create_list_store,
    list_view_key_handler,
    update_list_store,
)

new_builder = new_resource_builder("gaphor.UML.actions")


class ActivityParameterNodeView(GObject.Object):
    __gtype_name__ = "ActivityParameterNodeView"

    def __init__(self, node: UML.ActivityParameterNode | None, activity: UML.Activity):
        super().__init__()
        self.node = node
        self.activity = activity

    editing = GObject.Property(type=bool, default=False)

    @GObject.Property(type=str)
    def parameter(self) -> str:
        return format(self.node.parameter) if self.node else ""

    @parameter.setter  # type: ignore[no-redef]
    @transactional
    def parameter(self, value):
        if not self.node:
            if not value:
                return

            model = self.activity.model
            node = model.create(UML.ActivityParameterNode)
            node.parameter = model.create(UML.Parameter)
            self.node = node
            self.activity.node = node
        parse(self.node.parameter, value)

    def start_editing(self):
        self.editing = True

    def empty(self):
        return not self.node

    def unlink(self):
        if self.node:
            self.node.unlink()

    def swap(self, item1, item2):
        return self.activity.node.swap(item1.node, item2.node)


def activity_parameter_node_model(activity: UML.Activity) -> Gio.ListModel:
    return create_list_store(
        ActivityParameterNodeView,
        (
            node
            for node in activity.node
            if isinstance(node, UML.ActivityParameterNode) and node.parameter
        ),
        lambda node: ActivityParameterNodeView(node, activity),
    )


def update_activity_parameter_node_model(
    store: Gio.ListStore, activity: UML.Activity
) -> Gio.ListStore:
    return update_list_store(
        store,
        lambda item: item.node,
        (
            node
            for node in activity.node
            if isinstance(node, UML.ActivityParameterNode) and node.parameter
        ),
        lambda node: ActivityParameterNodeView(node, activity),
    )


@PropertyPages.register(ActivityItem)
class ActivityItemPage(PropertyPageBase):
    order = 40

    def __init__(self, item: ActivityItem):
        self.item = item
        self.watcher = item.subject and item.subject.watcher()

    def construct(self):
        subject = self.item.subject

        if not subject:
            return

        builder = new_builder(
            "activity-editor",
            "parameters-info",
            signals={
                "list-view-key-pressed": (list_view_key_handler,),
                "parameters-info-clicked": (self.on_parameters_info_clicked,),
            },
        )

        self.info = builder.get_object("parameters-info")
        help_link(builder, "parameters-info-icon", "parameters-info")

        list_view: Gtk.ListView = builder.get_object("parameter-list")

        self.model = activity_parameter_node_model(subject)
        selection = Gtk.SingleSelection.new(self.model)
        list_view.set_model(selection)

        list_view.set_factory(list_item_factory())

        if self.watcher:
            self.watcher.watch("node", self.on_nodes_changed)

        return unsubscribe_all_on_destroy(
            builder.get_object("activity-editor"), self.watcher
        )

    @event_handler(AssociationUpdated)
    def on_nodes_changed(self, event):
        update_activity_parameter_node_model(self.model, self.item.subject)

    def on_parameters_info_clicked(self, image, event):
        self.info.set_visible(True)


def list_item_factory():
    def on_double_click(ctrl, n_press, x, y):
        if n_press == 2:
            text = ctrl.get_widget()
            text.start_editing()

    def end_editing(list_item, should_commit):
        text = list_item.get_child()
        if should_commit:
            list_item.get_item().parameter = text.editable_text

    ui_string = translated_ui_string("gaphor.UML.actions", "parameter.ui")
    ui_bytes = GLib.Bytes.new(ui_string.encode("utf-8"))

    return Gtk.BuilderListItemFactory.new_from_bytes(
        Gtk.Builder.BuilderScope(
            {
                "on_double_click": on_double_click,
                "end_editing": end_editing,
            }
        ),
        ui_bytes,
    )


@PropertyPages.register(UML.ActivityParameterNode)
class ActivityParameterNodeNamePropertyPage(PropertyPageBase):
    """An adapter which works for any named item view.

    It also sets up a table view which can be extended.
    """

    order = 10

    def __init__(self, subject):
        assert subject is None or hasattr(subject, "name")
        super().__init__()
        self.subject = subject
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

    @transactional
    def _on_name_changed(self, entry):
        if self.subject.parameter.name != entry.get_text():
            self.subject.parameter.name = entry.get_text()
