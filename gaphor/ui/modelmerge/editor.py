from __future__ import annotations

from gaphas.decorators import nonrecursive
from gi.repository import Gio, Gtk

from gaphor.core import event_handler
from gaphor.core.changeset.apply import applicable, apply_change
from gaphor.core.modeling import ModelReady, PendingChange
from gaphor.event import (
    TransactionBegin,
    TransactionCommit,
    TransactionRollback,
)
from gaphor.i18n import translated_ui_string
from gaphor.transaction import Transaction
from gaphor.ui.modelmerge.organize import Node, organize_changes


class ModelMerge:
    def __init__(self, event_manager, element_factory, modeling_language):
        self.element_factory = element_factory
        self.event_manager = event_manager
        self.modeling_language = modeling_language
        self.model = Gio.ListStore.new(Node.__gtype__)
        self.selection = None
        self.tree_view = None
        self._tx_depth = 0

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

        factory = Gtk.SignalListItemFactory.new()
        factory.connect("setup", list_item_factory_setup, self.apply)

        self.tree_view = builder.get_object("modelmerge")
        self.tree_view.set_model(self.selection)
        self.tree_view.set_factory(factory)

        resolve = builder.get_object("modelmerge-resolve")
        resolve.connect("clicked", self.on_resolve_merge)

        self.event_manager.subscribe(self.on_model_loaded)

        self.refresh_model()

    def close(self):
        self.event_manager.unsubscribe(self.on_model_loaded)
        self.event_manager.unsubscribe(self.on_model_updated)

    @nonrecursive
    def apply(self, change_node: Node | None):
        def do_apply(node):
            for element in node.elements:
                if applicable(element, self.element_factory):
                    apply_change(element, self.element_factory, self.modeling_language)
            if node.children:
                for n in node.children:
                    do_apply(n)

        if change_node:
            with Transaction(self.event_manager):
                do_apply(change_node)

        for item in self.model:
            item.sync()

    def on_resolve_merge(self, _button):
        pending_changes = self.element_factory.lselect(PendingChange)
        self.model.remove_all()
        with Transaction(self.event_manager):
            for change in pending_changes:
                change.unlink()
        self.close()

    @event_handler(ModelReady)
    def on_model_loaded(self, event):
        self.event_manager.subscribe(self.on_model_updated)
        self.refresh_model()

    @event_handler(TransactionBegin, TransactionCommit, TransactionRollback)
    def on_model_updated(self, event):
        self._tx_depth += +1 if isinstance(event, TransactionBegin) else -1
        if self._tx_depth == 0:
            self.apply(None)


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
        if button.get_active() and button.get_sensitive() and not node.applied:
            on_apply(node)

    apply.connect("notify::active", on_active)

    # TODO: popup
