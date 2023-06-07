from __future__ import annotations

from gi.repository import GLib, GObject, Gio, Gtk

from gaphor import UML
from gaphor.action import action
from gaphor.core import transactional
from gaphor.core.format import format, parse
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    help_link,
    new_resource_builder,
    unsubscribe_all_on_destroy,
)
from gaphor.i18n import translated_ui_string
from gaphor.UML.actions.activity import ActivityItem

from gaphor.ui.actiongroup import create_action_group

START_EDIT_DELAY = 100


def create_shortcut_controller(shortcuts):
    ctrl = Gtk.ShortcutController.new_for_model(shortcuts)
    ctrl.set_scope(Gtk.ShortcutScope.LOCAL)
    return ctrl


new_builder = new_resource_builder("gaphor.UML.actions")


class ActivityParameterNodeView(GObject.Object):
    __gtype_name__ = "ActivityParameterNodeView"

    def __init__(self, node: UML.ActivityParameterNode | None, activity: UML.Activity):
        super().__init__()
        self.node = node
        self.activity = activity

    mode = GObject.Property(type=str, default="readonly")

    @GObject.Property(type=str)
    def parameter(self) -> str:
        return format(self.node.parameter) if self.node else ""

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

    def start_editing(self):
        self.mode = "editing"


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
        self.selection = Gtk.SingleSelection.new(self.model)
        list_view.set_model(self.selection)

        factory = Gtk.SignalListItemFactory.new()
        factory.connect(
            "setup",
            list_item_factory_setup,
        )

        list_view.set_factory(factory)

        action_group, shortcuts = create_action_group(self, "parameter")
        list_view.insert_action_group("parameter", action_group)
        list_view.add_controller(create_shortcut_controller(shortcuts))

        return unsubscribe_all_on_destroy(
            builder.get_object("activity-editor"), self.watcher
        )

    def on_parameters_info_clicked(self, image, event):
        self.info.set_visible(True)

    @action(name="parameter.rename", shortcut="F2")
    def _list_view_rename_selected(self):
        if view := self.selection.get_selected_item():
            GLib.timeout_add(START_EDIT_DELAY, view.start_editing)


def list_item_factory_setup(_factory, list_item):
    builder = Gtk.Builder()
    builder.set_current_object(list_item)
    builder.extend_with_template(
        list_item,
        type(list_item).__gtype__,
        translated_ui_string("gaphor.UML.actions", "parameter.ui"),
        -1,
    )

    def end_editing(text, pspec):
        if not text.props.editing:
            list_item.get_item().mode = "readonly"
            list_item.get_item().parameter = text.get_text()

    text = builder.get_object("text")
    text.connect("notify::editing", end_editing)
