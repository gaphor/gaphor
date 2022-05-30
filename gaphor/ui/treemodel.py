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

no_owner = object()


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
            if hasattr(model, "child_model"):
                return model.child_model
            if model and isinstance(model, Gio.ListModel):
                return (
                    RelationshipsModel(model)
                    if isinstance(model.element, UML.Package)
                    else model
                )
            return None

        tree_model = Gtk.TreeListModel.new(
            self.model,
            passthrough=False,
            autoexpand=True,
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

    def tree_model_for_element(self, element: Element | None) -> TreeModel | None:
        """Get the tree model for an element.

        Creates tree models and items if they do not exist.
        """
        if element is None:
            return self.model

        if (owner_model := self.tree_model_for_element(element.owner)) is not None:
            return owner_model.tree_model_for_element(element)
        return None

    def add_element(self, element, owner=no_owner):
        if (
            visible(element)
            and (
                model := self.tree_model_for_element(
                    element.owner if owner is no_owner else owner
                )
            )
            is not None
        ):
            first_element = not bool(model)
            model.add_element(element)
            if (
                first_element
                and model.element
                and (owner_model := self.tree_model_for_element(model.element.owner))
                is not None
            ):
                owner_model.items_changed(owner_model.items.index(model), 1, 1)

    def remove_element(self, element, owner=no_owner):
        if (
            visible(element)
            and (
                model := self.tree_model_for_element(
                    element.owner if owner is no_owner else owner
                )
            )
            is not None
        ):
            model.remove_element(element)
            last_element = not bool(model)
            if (
                last_element
                and model.element
                and (owner_model := self.tree_model_for_element(model.element.owner))
            ):
                owner_model.items_changed(owner_model.items.index(model), 1, 1)

    @event_handler(ElementCreated)
    def on_element_created(self, event: ElementCreated):
        self.add_element(event.element)

    @event_handler(ElementDeleted)
    def on_element_deleted(self, event: ElementDeleted):
        self.remove_element(event.element)

    @event_handler(DerivedSet)
    def on_owner_changed(self, event: DerivedSet):
        if (event.property is not Element.owner) or not visible(event.element):
            return

        old_value, new_value = event.old_value, event.new_value
        element = event.element

        self.remove_element(element, owner=old_value)
        self.add_element(element, owner=new_value)

    @event_handler(AttributeUpdated)
    def on_attribute_changed(self, event: AttributeUpdated):
        element = event.element

        if (
            visible(element)
            and (model := self.tree_model_for_element(element)) is not None
        ):
            model.sync()

    @event_handler(ModelReady, ModelFlushed)
    def on_model_ready(self, event=None):
        model = self.model
        model.clear()

        for element in self.element_factory.select(
            lambda e: (e.owner is None) and visible(e)
        ):
            model.add_element(element)


def new_list_item_ui():
    b = translated_ui_string("gaphor.ui", "treeitem.ui")
    return GLib.Bytes.new(b.encode("utf-8"))


def visible(element):
    return isinstance(
        element, (UML.Relationship, UML.NamedElement, Diagram)
    ) and not isinstance(
        element, (UML.InstanceSpecification, UML.OccurrenceSpecification)
    )


class TreeModel(GObject.Object, Gio.ListModel):
    def __init__(self, element):
        super().__init__()
        self.element = element
        self.items: list[TreeModel] = (
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

    def do_get_item(self, position) -> TreeModel | None:
        try:
            return self.items[position]  # type: ignore[no-any-return]
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


class RelationshipsModel(GObject.Object, Gio.ListModel):
    """Filter relationships from the model and show them in a child model."""

    def __init__(self, model):
        super().__init__()
        self.relationships = Gtk.FilterListModel.new(
            model, Gtk.CustomFilter.new(uml_relationship_matcher)
        )
        self.others = Gtk.FilterListModel.new(
            model, Gtk.CustomFilter.new(negating_matcher(uml_relationship_matcher))
        )
        self.relationships.connect("items-changed", self.on_relationships_changed)
        self.others.connect("items-changed", self.on_others_changed)

        self.has_relationships = 1 if self.relationships else 0
        self.relationships_item = TreeModel(None)
        self.relationships_item.text = gettext("<Relationships>")
        self.relationships_item.child_model = self.relationships

    def on_others_changed(self, _model, position, removed, added):
        self.items_changed(position + self.has_relationships, removed, added)

    def on_relationships_changed(self, _model, position, removed, added):
        if self.has_relationships and not self.relationships.get_n_items():
            self.has_relationships = 0
            self.items_changed(0, 1, 0)
        elif (not self.has_relationships) and self.relationships.get_n_items():
            self.has_relationships = 1
            self.items_changed(0, 0, 1)

    def do_get_item_type(self) -> GObject.GType:
        return self.others.get_item_type()

    def do_get_n_items(self) -> int:
        return self.others.get_n_items() + self.has_relationships  # type: ignore[no-any-return]

    def do_get_item(self, position) -> TreeModel:
        if position == 0 and self.has_relationships:
            return self.relationships_item
        return self.others.get_item(position - self.has_relationships)  # type: ignore[no-any-return]


def uml_relationship_matcher(item):
    return isinstance(item, TreeModel) and isinstance(item.element, UML.Relationship)


def negating_matcher(matcher):
    return lambda item: not matcher(item)
