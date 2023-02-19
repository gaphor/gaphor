from __future__ import annotations

from gi.repository import Gio, GObject, Gtk

from gaphor.event import ModelLoaded
from gaphor.core.modeling import PendingChange, ElementChange
from gaphor.i18n import translated_ui_string
from gaphor.ui.abc import UIComponent
from gaphor.core import event_handler


class ChangeSetModel:
    def __init__(self, element_factory):
        self.element_factory = element_factory
        self.root = Gio.ListStore.new(ChangeItem.__gtype__)

    def update(self):
        for element in self.element_factory.select(PendingChange):
            change_item = ChangeItem(element)
            self.root.append(change_item)

    def child_model(self, item: ChangeItem, _user_data=None):
        return None


class ModelMerge(UIComponent):
    def __init__(self, event_manager, element_factory):
        self.element_factory = element_factory
        self.event_manager = event_manager
        self.model = ChangeSetModel(element_factory)
        self.selection = None
        self.tree_view = None
        event_manager.subscribe(self.on_model_loaded)

    def shutdown(self):
        self.event_manager.unsubscribe(self.on_model_loaded)

    @event_handler(ModelLoaded)
    def on_model_loaded(self, event):
        self.model.update()

    def open(self):
        tree_model = Gtk.TreeListModel.new(
            self.model.root,
            passthrough=False,
            autoexpand=False,
            create_func=self.model.child_model,
            user_data=None,
        )

        self.selection = Gtk.SingleSelection.new(tree_model)

        factory = Gtk.SignalListItemFactory.new()
        factory.connect("setup", list_item_factory_setup)
        self.tree_view = Gtk.ListView.new(self.selection, factory)
        self.tree_view.set_vexpand(True)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_child(self.tree_view)

        return scrolled_window

    def close(self):
        pass


class ChangeItem(GObject.Object):
    def __init__(self, element: PendingChange):
        super().__init__()
        self.element = element
        self.sync()

    label = GObject.Property(type=str, default="Foo bar")
    # Setter is handled via a signal connect, somehow setters do not work for bool
    applied = GObject.Property(type=bool, default=False)

    def sync(self) -> None:
        element = self.element
        self.label = (
            element.element_name
            if isinstance(element, ElementChange)
            else element.property_name  # type: ignore[attr-defined]
        )
        self.applied = element.applied or False


def list_item_factory_setup(_factory, list_item):
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
        list_item.get_item().get_item().element.applied = button.get_active()

    apply.connect("notify::active", on_active)
