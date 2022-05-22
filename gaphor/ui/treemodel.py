from __future__ import annotations

from gi.repository import Gio, GLib, GObject, Gtk

from gaphor.abc import ActionProvider
from gaphor.core import event_handler
from gaphor.core.modeling import ElementCreated
from gaphor.core.modeling.event import ElementDeleted
from gaphor.diagram.iconname import get_icon_name
from gaphor.i18n import gettext, translated_ui_string
from gaphor.ui.abc import UIComponent


class TreeItem(GObject.GObject):
    def __init__(self, element):
        super().__init__()
        self.element = element
        self._text = format(element) or gettext("<None>")
        self._icon = get_icon_name(element)
        self.child_model = None

    @GObject.Property(type=str)
    def text(self):
        return self._text

    @text.setter  # type: ignore[no-redef]
    def text(self, text):
        self._text = text

    @GObject.Property(type=str)
    def icon(self):
        return self._name


class TreeModel(GObject.Object, Gio.ListModel):
    def __init__(self, element_factory, owner):
        super().__init__()
        self.items = [TreeItem(e) for e in element_factory.select() if e.owner is owner]

    def add_element(self, element):
        self.items.append(TreeItem(element))
        self.items_changed(len(self.items), 0, 1)

    def remove_element(self, element):
        index = next(i for i, e in enumerate(self.items) if e.element is element)
        del self.items[index]
        self.items_changed(index, 1, 0)

    def do_get_item_type(self) -> GObject.GType:
        return TreeItem.__gtype__

    def do_get_n_items(self) -> int:
        return len(self.items)

    def do_get_item(self, position) -> GObject.Object | None:
        try:
            return self.items[position]
        except IndexError:
            return None


def new_list_item_ui():
    b = translated_ui_string("gaphor.ui", "treeitem.ui")
    return GLib.Bytes.new(b.encode("utf-8"))


class TreeComponent(UIComponent, ActionProvider):
    def __init__(self, event_manager, element_factory):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.model = TreeModel(self.element_factory, owner=None)

    def open(self):
        self.event_manager.subscribe(self.on_element_create)
        self.event_manager.subscribe(self.on_element_delete)

        def child_model(item, user_data):
            if not item.child_model:
                item.child_model = TreeModel(self.element_factory, owner=item.element)
            return item.child_model

        tree = Gtk.TreeListModel.new(
            self.model,
            passthrough=False,
            autoexpand=False,
            create_func=child_model,
            user_data=None,
        )

        selection = Gtk.SingleSelection.new(tree)
        factory = Gtk.BuilderListItemFactory.new_from_bytes(None, new_list_item_ui())

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_child(Gtk.ListView.new(selection, factory))
        return scrolled_window

    def close(self):
        self.event_manager.unsubscribe(self.on_element_create)
        self.event_manager.unsubscribe(self.on_element_delete)

    @event_handler(ElementCreated)
    def on_element_create(self, event):
        self.model.add_element(event.element)

    @event_handler(ElementDeleted)
    def on_element_delete(self, event):
        self.model.remove_element(event.element)
