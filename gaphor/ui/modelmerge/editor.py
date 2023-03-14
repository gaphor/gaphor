from __future__ import annotations

from gi.repository import Gio, Gtk

from gaphor.event import ModelLoaded
from gaphor.core.modeling import PendingChange, AttributeUpdated
from gaphor.core.changeset.apply import apply_change
from gaphor.i18n import translated_ui_string
from gaphor.ui.abc import UIComponent
from gaphor.core import event_handler
from gaphor.transaction import Transaction
from gaphor.ui.modelmerge.organize import organize_changes, Node


class ModelMerge(UIComponent):
    def __init__(self, event_manager, element_factory, modeling_language):
        self.element_factory = element_factory
        self.event_manager = event_manager
        self.modeling_language = modeling_language
        self.model = Gio.ListStore.new(Node.__gtype__)
        self.selection = None
        self.tree_view = None
        self.scrolled_window = None
        event_manager.subscribe(self.on_model_loaded)
        event_manager.subscribe(self.on_pending_change)

    def shutdown(self):
        self.event_manager.unsubscribe(self.on_model_loaded)
        self.event_manager.unsubscribe(self.on_pending_change)

    def refresh_model(self):
        self.model.remove_all()

        for node in organize_changes(self.element_factory):
            self.model.append(node)

    @event_handler(ModelLoaded)
    def on_model_loaded(self, event):
        self.refresh_model()
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
            self.model,
            passthrough=False,
            autoexpand=True,
            create_func=lambda node, _: node.children,
            user_data=None,
        )

        self.selection = Gtk.SingleSelection.new(tree_model)

        def on_apply(change_node: Node):
            if not change_node.elements:
                return
            with Transaction(self.event_manager):
                for element in change_node.elements:
                    apply_change(element, self.element_factory, self.modeling_language)

        factory = Gtk.SignalListItemFactory.new()
        factory.connect("setup", list_item_factory_setup, on_apply)
        self.tree_view = Gtk.ListView.new(self.selection, factory)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_child(self.tree_view)

        self.scrolled_window = scrolled_window
        self.scrolled_window.set_visible(bool(self.model))

        return scrolled_window

    def close(self):
        pass


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
        node = list_item.get_item().get_item()
        if button.get_active() and node:
            on_apply(node)
        node.sync()

    apply.connect("notify::active", on_active)
