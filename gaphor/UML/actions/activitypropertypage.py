from __future__ import annotations

from gi.repository import GLib, GObject, Gio, Gtk

from gaphor import UML
from gaphor.core import transactional
from gaphor.core.format import parse
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    help_link,
    new_resource_builder,
    unsubscribe_all_on_destroy,
)
from gaphor.i18n import translated_ui_string
from gaphor.UML.actions.activity import ActivityItem

new_builder = new_resource_builder("gaphor.UML.actions")


class ActivityParameterNodeView(GObject.Object):
    def __init__(self, node: UML.ActivityParameterNode | None, activity: UML.Activity):
        super().__init__()
        self.node = node
        self.activity = activity

    @GObject.Property(type=str)
    def parameter(self) -> str:
        return self.node.parameter.name  # format(self.node.parameter)

    @parameter.setter  # type: ignore[no-redef]
    @transactional
    def parameter(self, value):
        if not self.node:
            model = self.activity.model
            node = model.create(UML.ActivityParameterNode)
            node.parameter = model.create(UML.Parameter)
            self.node = node
            self.activity.node = node
        parse(self.node.parameter, value)


def activity_parameter_node_model(activity: UML.Activity) -> Gio.ListModel:
    store = Gio.ListStore.new(ActivityParameterNodeView)

    for node in activity.node:
        if isinstance(node, UML.ActivityParameterNode) and node.parameter:
            store.append(ActivityParameterNodeView(node, activity))
    store.append(ActivityParameterNodeView(None, activity))

    return store


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
                "parameters-info-clicked": (self.on_parameters_info_clicked),
            },
        )

        self.info = builder.get_object("parameters-info")
        help_link(builder, "parameters-info-icon", "parameters-info")

        list_view: Gtk.ListView = builder.get_object("parameter-list")

        self.model = activity_parameter_node_model(subject)
        selection = Gtk.SingleSelection.new(self.model)
        list_view.set_model(selection)

        list_item_ui = translated_ui_string(
            "gaphor.UML.actions", "parameter.ui"
        ).encode("utf-8")
        factory = Gtk.BuilderListItemFactory.new_from_bytes(
            Gtk.BuilderCScope.new(), GLib.Bytes.new(list_item_ui)
        )
        list_view.set_factory(factory)

        # controller = Gtk.EventControllerKey.new()
        # list_view.add_controller(controller)
        # controller.connect("key-pressed", on_keypress_event, list_view)

        return unsubscribe_all_on_destroy(
            builder.get_object("activity-editor"), self.watcher
        )

    def on_parameters_info_clicked(self, image, event):
        self.info.set_visible(True)
