from __future__ import annotations

from gi.repository import Gio, Gtk

from gaphor.event import ModelLoaded
from gaphor.core.modeling import PendingChange
from gaphor.core.changeset.apply import apply_change, applicable
from gaphor.i18n import translated_ui_string
from gaphor.core import event_handler
from gaphor.transaction import Transaction
from gaphor.ui.modelmerge.organize import organize_changes, Node


class ModelMerge:
    def __init__(self, event_manager, element_factory, modeling_language):
        self.element_factory = element_factory
        self.event_manager = event_manager
        self.modeling_language = modeling_language
        self.model = Gio.ListStore.new(Node.__gtype__)
        self.selection = None
        self.tree_view = None

    @property
    def needs_merge(self):
        return bool(next(self.element_factory.select(PendingChange), None))

    def refresh_model(self):
        self.model.remove_all()

        for node in organize_changes(self.element_factory, self.modeling_language):
            self.model.append(node)

    def open(self, builder):
        tree_model = Gtk.TreeListModel.new(
            self.model,
            passthrough=False,
            autoexpand=False,
            create_func=lambda node, _: node.children,
            user_data=None,
        )

        self.selection = Gtk.SingleSelection.new(tree_model)

        def on_apply(change_node: Node, sync=True):
            if not change_node.elements:
                return

            with Transaction(self.event_manager):
                for element in change_node.elements:
                    if applicable(element, self.element_factory):
                        apply_change(
                            element, self.element_factory, self.modeling_language
                        )
                if change_node.children:
                    for n in change_node.children:
                        on_apply(n, sync=False)

            if sync:
                for item in self.model:
                    item.sync()

        factory = Gtk.SignalListItemFactory.new()
        factory.connect("setup", list_item_factory_setup, on_apply)

        self.tree_view = builder.get_object("modelmerge")
        self.tree_view.set_model(self.selection)
        self.tree_view.set_factory(factory)

        resolve = builder.get_object("modelmerge-resolve")
        resolve.connect("clicked", self.on_resolve_merge)

        self.event_manager.subscribe(self.on_model_loaded)

        self.refresh_model()

    def close(self):
        self.event_manager.unsubscribe(self.on_model_loaded)

    def on_resolve_merge(self, _button):
        pending_changes = self.element_factory.lselect(PendingChange)
        self.model.remove_all()
        with Transaction(self.event_manager):
            for change in pending_changes:
                change.unlink()

    @event_handler(ModelLoaded)
    def on_model_loaded(self, event):
        self.refresh_model()


def list_item_factory_setup(_factory, list_item, on_apply):
    builder = Gtk.Builder()
    builder.set_current_object(list_item)
    builder.extend_with_template(
        list_item,
        type(list_item).__gtype__,
        translated_ui_string("gaphor.ui.modelmerge", "change.ui"),
        -1,
    )
    apply = builder.get_object("apply")

    def on_active(button, _gparam):
        node = list_item.get_item().get_item()
        if button.get_active() and node:
            on_apply(node)
        node.sync()

    apply.connect("notify::active", on_active)
