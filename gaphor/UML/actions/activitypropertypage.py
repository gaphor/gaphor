from __future__ import annotations

from gi.repository import GObject, Gio, Gdk, Gtk

from gaphor import UML
from gaphor.core import transactional, event_handler
from gaphor.core.format import format, parse
from gaphor.core.modeling import AssociationUpdated
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
    __gtype_name__ = "ActivityParameterNodeView"

    def __init__(self, node: UML.ActivityParameterNode | None, activity: UML.Activity):
        super().__init__()
        self.node = node
        self.activity = activity

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


def activity_parameter_node_model(activity: UML.Activity) -> Gio.ListModel:
    store = Gio.ListStore.new(ActivityParameterNodeView)

    for node in activity.node:
        if isinstance(node, UML.ActivityParameterNode) and node.parameter:
            store.append(ActivityParameterNodeView(node, activity))
    store.append(ActivityParameterNodeView(None, activity))

    return store


def update_activity_parameter_node_model(
    store: Gio.ListStore, activity: UML.Activity
) -> None:
    n = 0
    for node in activity.node:
        if node is not store.get_item(n).node:
            store.remove(n)
            store.insert(n, ActivityParameterNodeView(node, activity))
        n += 1

    while store.get_n_items() > n:
        store.remove(store.get_n_items() - 1)

    if (
        not store.get_n_items()
        or store.get_item(store.get_n_items() - 1).node is not None
    ):
        store.append(ActivityParameterNodeView(None, activity))


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
        list_view.add_controller(keyboard_shortcuts(selection))

        factory = Gtk.SignalListItemFactory.new()
        factory.connect(
            "setup",
            list_item_factory_setup,
        )

        list_view.set_factory(factory)

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
            list_item.get_item().parameter = text.get_text()

    text = builder.get_object("text")
    text.connect("notify::editing", end_editing)


def keyboard_shortcuts(selection):
    ctrl = Gtk.EventControllerKey.new()
    ctrl.connect("key-pressed", list_view_handler, selection)
    return ctrl


@transactional
def list_view_handler(_list_view, keyval, _keycode, state, selection):
    item = selection.get_selected_item()
    if not (item and item.node):
        return False

    if keyval in (Gdk.KEY_Delete, Gdk.KEY_BackSpace) and not state & (
        Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK
    ):
        item.node.unlink()
        return True

    elif keyval in (Gdk.KEY_equal, Gdk.KEY_plus, Gdk.KEY_minus, Gdk.KEY_underscore):
        pos = selection.get_selected()
        swap_pos = pos + 1 if keyval in (Gdk.KEY_equal, Gdk.KEY_plus) else pos - 1
        if not 0 <= swap_pos < selection.get_n_items():
            return False

        other = selection.get_item(swap_pos)
        if not (other and other.node):
            return False

        if item.activity.node.swap(item.node, other.node):
            selection.set_selected(swap_pos)
        return True
    return False
