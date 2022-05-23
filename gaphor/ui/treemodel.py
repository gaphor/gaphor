from __future__ import annotations

from gi.repository import Gio, GLib, GObject, Gtk

from gaphor import UML
from gaphor.abc import ActionProvider
from gaphor.core import event_handler
from gaphor.core.modeling import (
    DerivedSet,
    Diagram,
    Element,
    ElementCreated,
    ElementDeleted,
)
from gaphor.diagram.iconname import get_icon_name
from gaphor.i18n import gettext, translated_ui_string
from gaphor.ui.abc import UIComponent


class TreeItem(GObject.GObject):
    def __init__(self, element: Element):
        super().__init__()
        self.element = element
        self._text = format(element) or gettext("<None>")
        self._icon = get_icon_name(element)
        self._child_model: TreeModel | None = None

    @property
    def child_model(self) -> TreeModel:
        if not self._child_model:
            self._child_model = TreeModel(owner=self.element)
        return self._child_model

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
    def __init__(self, owner):
        super().__init__()
        self.items = (
            [TreeItem(e) for e in owner.ownedElement if e.owner is owner]
            if owner
            else []
        )

    def add_element(self, element: Element) -> None:
        self.items.append(TreeItem(element))
        self.items_changed(len(self.items), 0, 1)

    def remove_element(self, element: Element) -> None:
        index = next(i for i, ti in enumerate(self.items) if ti.element is element)
        del self.items[index]
        self.items_changed(index, 1, 0)

    def tree_item_for_element(self, element) -> TreeItem:
        return next(ti for ti in self.items if ti.element is element)

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
        self.model = TreeModel(owner=None)

    def open(self):
        self.event_manager.subscribe(self.on_element_create)
        self.event_manager.subscribe(self.on_element_delete)
        self.event_manager.subscribe(self.on_association_set)

        def child_model(item, user_data):
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
        self.event_manager.subscribe(self.on_association_set)

    def _visible(self, element):
        return isinstance(
            element, (UML.Relationship, UML.NamedElement, Diagram)
        ) and not isinstance(
            element, (UML.InstanceSpecification, UML.OccurrenceSpecification)
        )

    def tree_model_for_element(self, element: Element | None) -> TreeModel:
        if element is None:
            return self.model
        owner = element.owner
        owner_model = self.tree_model_for_element(owner)
        tree_item = owner_model.tree_item_for_element(element)
        return tree_item.child_model

    @event_handler(ElementCreated)
    def on_element_create(self, event):
        element = event.element
        if self._visible(element):
            model = self.tree_model_for_element(element.owner)
            model.add_element(element)

    @event_handler(ElementDeleted)
    def on_element_delete(self, event):
        element = event.element
        if self._visible(element):
            model = self.tree_model_for_element(element.owner)
            model.remove_element(element)

    @event_handler(DerivedSet)
    def on_association_set(self, event):
        if event.property is not Element.owner:
            return

        old_value, new_value = event.old_value, event.new_value
        element = event.element

        old_tree_model = self.tree_model_for_element(old_value)
        old_tree_model.remove_element(element)

        if self._visible(element):
            new_tree_model = self.tree_model_for_element(new_value)
            new_tree_model.add_element(element)
