from __future__ import annotations

from gi.repository import Gio, GObject, Gtk

from gaphor.event import ModelLoaded
from gaphor.core.modeling import PendingChange, AttributeUpdated
from gaphor.core.changeset.apply import apply_change, applicable
from gaphor.i18n import translated_ui_string
from gaphor.ui.abc import UIComponent
from gaphor.core import event_handler
from gaphor.transaction import Transaction
from gaphor.core.changeset.organize import organize_changes, Node


class ChangeSetModel:
    def __init__(self, element_factory):
        self.element_factory = element_factory
        self.root = Gio.ListStore.new(ChangeItem.__gtype__)
        self.child_models = {}

    def update(self):
        self.root.remove_all()
        self.child_models.clear()

        def update_child_models(node):
            if not node.children:
                return
            store = self.child_models[node] = Gio.ListStore.new(ChangeItem.__gtype__)
            for n in node.children:
                store.append(ChangeItem(n))

        for node in organize_changes(self.element_factory):
            update_child_models(node)
            self.root.append(ChangeItem(node))

    def child_model(self, item: ChangeItem, _user_data=None):
        return self.child_models.get(item.node)

    def __iter__(self):
        return iter(self.root)


class ModelMerge(UIComponent):
    def __init__(self, event_manager, element_factory, modeling_language):
        self.element_factory = element_factory
        self.event_manager = event_manager
        self.modeling_language = modeling_language
        self.model = ChangeSetModel(element_factory)
        self.selection = None
        self.tree_view = None
        self.scrolled_window = None
        event_manager.subscribe(self.on_model_loaded)
        event_manager.subscribe(self.on_pending_change)

    def shutdown(self):
        self.event_manager.unsubscribe(self.on_model_loaded)
        self.event_manager.unsubscribe(self.on_pending_change)

    @event_handler(ModelLoaded)
    def on_model_loaded(self, event):
        self.model.update()
        if self.scrolled_window and next(
            self.element_factory.select(PendingChange), None
        ):
            self.scrolled_window.set_visible(True)

    @event_handler(AttributeUpdated)
    def on_pending_change(self, event):
        if event.property is PendingChange.applied:
            for item in self.model:
                item.sync()

    def open(self):
        tree_model = Gtk.TreeListModel.new(
            self.model.root,
            passthrough=False,
            autoexpand=True,
            create_func=self.model.child_model,
            user_data=None,
        )

        self.selection = Gtk.SingleSelection.new(tree_model)

        def on_apply(change_node):
            if not change_node.element:
                return
            with Transaction(self.event_manager):
                apply_change(
                    change_node.element, self.element_factory, self.modeling_language
                )

        factory = Gtk.SignalListItemFactory.new()
        factory.connect("setup", list_item_factory_setup, on_apply)
        self.tree_view = Gtk.ListView.new(self.selection, factory)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_child(self.tree_view)

        self.scrolled_window = scrolled_window
        self.scrolled_window.set_visible(bool(self.model.root))

        return scrolled_window

    def close(self):
        pass


class ChangeItem(GObject.Object):
    def __init__(self, node: Node):
        super().__init__()
        self.node = node
        self.label = node.text
        self.sync()

    label = GObject.Property(type=str, default="Foo bar")
    applied = GObject.Property(type=bool, default=True)
    applicable = GObject.Property(type=bool, default=True)

    def sync(self) -> None:
        element = self.node.element
        if not isinstance(element, PendingChange):
            return
        self.applicable = not element.applied and applicable(element, element.model)
        self.applied = bool(element.applied)


def list_item_factory_setup(_factory, list_item, on_apply):
    builder = Gtk.Builder()
    builder.set_current_object(list_item)
    builder.extend_with_template(
        list_item,
        type(list_item).__gtype__,
        translated_ui_string("gaphor.ui", "change.ui"),
        -1,
    )
    apply = builder.get_object("apply")

    def on_active(button, _gparam):
        change_item = list_item.get_item().get_item()
        if button.get_active() and change_item.node:
            on_apply(change_item.node)
        change_item.sync()

    apply.connect("notify::active", on_active)
