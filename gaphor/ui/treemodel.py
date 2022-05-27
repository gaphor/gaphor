from __future__ import annotations

from gi.repository import Gio, GLib, GObject, Gtk, Pango

from gaphor import UML
from gaphor.abc import ActionProvider
from gaphor.core import event_handler
from gaphor.core.format import format
from gaphor.core.modeling import (
    DerivedSet,
    Diagram,
    Element,
    ElementCreated,
    ElementDeleted,
    ModelFlushed,
    ModelReady,
)
from gaphor.core.modeling.event import AttributeUpdated
from gaphor.diagram.iconname import get_icon_name
from gaphor.i18n import gettext, translated_ui_string
from gaphor.ui.abc import UIComponent


class TreeModel(GObject.Object, Gio.ListModel):
    def __init__(self, element):
        super().__init__()
        self.element = element
        self.items = (
            [
                TreeModel(e)
                for e in element.ownedElement
                if e.owner is element and visible(e)
            ]
            if element
            else []
        )
        if element:
            self.sync()

    text = GObject.Property(type=str)
    icon = GObject.Property(type=str)
    attributes = GObject.Property(type=Pango.AttrList)

    def add_element(self, element: Element) -> TreeModel:
        if existing := next((ti for ti in self.items if ti.element is element), None):
            return existing

        tree_item = TreeModel(element)
        self.items.append(tree_item)
        self.items_changed(len(self.items), 0, 1)
        return tree_item

    def remove_element(self, element: Element) -> None:
        index = next(
            (i for i, ti in enumerate(self.items) if ti.element is element), None
        )
        if index is None:
            return
        del self.items[index]
        self.items_changed(index, 1, 0)

    def sync(self) -> None:
        element = self.element
        assert element
        self.text = format(element) or gettext("<None>")
        self.icon = get_icon_name(element)
        self.attributes = pango_attributes(element)

    def clear(self) -> None:
        n = len(self.items)
        del self.items[:]
        self.items_changed(0, n, 0)

    def tree_model_for_element(self, element: Element | None) -> TreeModel | None:
        return next((m for m in self.items if m.element is element), None)

    def do_get_item_type(self) -> GObject.GType:
        return TreeModel.__gtype__

    def do_get_n_items(self) -> int:
        return len(self.items)

    def do_get_item(self, position) -> GObject.Object | None:
        try:
            return self.items[position]
        except IndexError:
            return None


def pango_attributes(element):
    attrs = Pango.AttrList.new()
    attrs.insert(
        Pango.attr_weight_new(
            Pango.Weight.BOLD if isinstance(element, Diagram) else Pango.Weight.NORMAL
        )
    )
    attrs.insert(
        Pango.attr_style_new(
            Pango.Style.ITALIC
            if isinstance(element, (UML.Classifier, UML.BehavioralFeature))
            and element.isAbstract
            else Pango.Style.NORMAL
        )
    )
    return attrs


class TreeComponent(UIComponent, ActionProvider):
    def __init__(self, event_manager, element_factory):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.model = TreeModel(element=None)

    def open(self):
        self.event_manager.subscribe(self.on_element_created)
        self.event_manager.subscribe(self.on_element_deleted)
        self.event_manager.subscribe(self.on_owner_changed)
        self.event_manager.subscribe(self.on_attribute_changed)
        self.event_manager.subscribe(self.on_model_ready)

        def child_model(model, _user_data):
            return model if model.items else None

        tree_model = Gtk.TreeListModel.new(
            self.model,
            passthrough=False,
            autoexpand=False,
            create_func=child_model,
            user_data=None,
        )

        # noqa: sorter = Gtk.StringSorter(Gtk.PropertyExpression.new(TreeItem.__gtype__, None, "text"))
        # noqa: tree_sorter = Gtk.TreeListRowSorter.new(sorter)
        # noqa: sort_model = Gtk.SortListModel.new(tree_model, tree_sorter)
        selection = Gtk.SingleSelection.new(tree_model)  # sort_model
        factory = Gtk.BuilderListItemFactory.new_from_bytes(None, new_list_item_ui())

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_child(Gtk.ListView.new(selection, factory))

        self.on_model_ready()

        return scrolled_window

    def close(self):
        self.event_manager.unsubscribe(self.on_element_created)
        self.event_manager.unsubscribe(self.on_element_deleted)
        self.event_manager.unsubscribe(self.on_owner_changed)
        self.event_manager.unsubscribe(self.on_attribute_changed)
        self.event_manager.unsubscribe(self.on_model_ready)

    def tree_model_for_element(self, element: Element | None) -> TreeModel:
        """Get the tree model for an element.

        Creates tree models and items if they do not exist.
        """
        if element is None:
            return self.model

        owner_model = self.tree_model_for_element(element.owner)

        if (model := owner_model.tree_model_for_element(element)) is None:
            model = owner_model.add_element(element)
            owner_model.items_changed(owner_model.items.index(model), 1, 1)

        return model

    @event_handler(ElementCreated)
    def on_element_created(self, event: ElementCreated):
        element = event.element
        if visible(element):
            model = self.tree_model_for_element(element.owner)
            assert model is not None
            model.add_element(element)

    @event_handler(ElementDeleted)
    def on_element_deleted(self, event: ElementDeleted):
        element = event.element
        if visible(element):
            model = self.tree_model_for_element(element.owner)
            assert model is not None
            model.remove_element(element)
            # TODO: if not model.items and model is not self.model: remove child model

    @event_handler(DerivedSet)
    def on_owner_changed(self, event: DerivedSet):
        if event.property is not Element.owner or not visible(event.element):
            return

        old_value, new_value = event.old_value, event.new_value
        element = event.element

        old_tree_model = self.tree_model_for_element(old_value)
        old_tree_model.remove_element(element)

        new_tree_model = self.tree_model_for_element(new_value)
        new_tree_model.add_element(element)

    @event_handler(AttributeUpdated)
    def on_attribute_changed(self, event: AttributeUpdated):
        element = event.element

        tree_model = self.tree_model_for_element(element)
        tree_model.sync()

    @event_handler(ModelReady, ModelFlushed)
    def on_model_ready(self, event=None):
        self.model.clear()

        for element in self.element_factory.select(visible):
            self.tree_model_for_element(element)


def new_list_item_ui():
    b = translated_ui_string("gaphor.ui", "treeitem.ui")
    return GLib.Bytes.new(b.encode("utf-8"))


def visible(element):
    return isinstance(
        element, (UML.Relationship, UML.NamedElement, Diagram)
    ) and not isinstance(
        element, (UML.InstanceSpecification, UML.OccurrenceSpecification)
    )
