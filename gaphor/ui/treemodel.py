from __future__ import annotations

from gaphas.decorators import g_async
from gi.repository import Gdk, Gio, GLib, GObject, Gtk, Pango

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
from gaphor.ui.event import DiagramSelectionChanged

no_owner = object()


class TreeItem(GObject.Object):
    def __init__(self, element):
        super().__init__()
        self.element = element
        if element:
            self.sync()

    text = GObject.Property(type=str)
    icon = GObject.Property(type=str)
    icon_visible = GObject.Property(type=bool, default=False)
    attributes = GObject.Property(type=Pango.AttrList)

    def sync(self) -> None:
        if element := self.element:
            self.text = format(element) or gettext("<None>")
            self.icon = get_icon_name(element)
            self.icon_visible = bool(
                self.icon
                and not isinstance(
                    element, (UML.Parameter, UML.Property, UML.Operation)
                )
            )
            self.attributes = pango_attributes(element)


class TreeComponent(UIComponent, ActionProvider):
    def __init__(self, event_manager, element_factory):
        self.event_manager = event_manager
        self.element_factory = element_factory
        self.model = TreeModel()

    def open(self):
        self.event_manager.subscribe(self.on_element_created)
        self.event_manager.subscribe(self.on_element_deleted)
        self.event_manager.subscribe(self.on_owner_changed)
        self.event_manager.subscribe(self.on_attribute_changed)
        self.event_manager.subscribe(self.on_model_ready)
        self.event_manager.subscribe(self.on_diagram_selection_changed)

        tree_model = Gtk.TreeListModel.new(
            self.model.root,
            passthrough=False,
            autoexpand=False,
            create_func=self.model.child_model,
            user_data=None,
        )

        self.sorter = Gtk.CustomSorter.new(tree_item_sort)
        tree_sorter = Gtk.TreeListRowSorter.new(self.sorter)
        self.sort_model = Gtk.SortListModel.new(tree_model, tree_sorter)
        self.selection = Gtk.SingleSelection.new(self.sort_model)
        factory = Gtk.SignalListItemFactory.new()
        factory.connect("setup", list_item_factory_setup)
        tree_view = Gtk.ListView.new(self.selection, factory)

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_window.set_child(tree_view)

        self.on_model_ready()

        return scrolled_window

    def close(self):
        self.event_manager.unsubscribe(self.on_element_created)
        self.event_manager.unsubscribe(self.on_element_deleted)
        self.event_manager.unsubscribe(self.on_owner_changed)
        self.event_manager.unsubscribe(self.on_attribute_changed)
        self.event_manager.unsubscribe(self.on_model_ready)
        self.event_manager.unsubscribe(self.on_diagram_selection_changed)

    @event_handler(ElementCreated)
    def on_element_created(self, event: ElementCreated):
        self.model.add_element(event.element)

    @event_handler(ElementDeleted)
    def on_element_deleted(self, event: ElementDeleted):
        self.model.remove_element(event.element)

    @event_handler(DerivedSet)
    def on_owner_changed(self, event: DerivedSet):
        if (event.property is not Element.owner) or not visible(event.element):
            return

        element = event.element
        self.model.remove_element(element, owner=event.old_value)
        self.model.add_element(element)
        self.focus_element(element)

    @event_handler(AttributeUpdated)
    def on_attribute_changed(self, event: AttributeUpdated):
        self.model.sync(event.element)
        self.sorter.changed(Gtk.SorterChange.DIFFERENT)

    @event_handler(ModelReady, ModelFlushed)
    def on_model_ready(self, event=None):
        model = self.model
        model.clear()

        for element in self.element_factory.select(
            lambda e: (e.owner is None) and visible(e)
        ):
            model.add_element(element)

    @event_handler(DiagramSelectionChanged)
    def on_diagram_selection_changed(self, event):
        if not event.focused_item:
            return
        element = event.focused_item.subject
        if not element:
            return

        self.focus_element(element)

    @g_async(single=True)
    def focus_element(self, element):
        def expand_up_to_element(element, expand=False):
            if not element:
                return 0
            n = expand_up_to_element(element.owner, expand=True)
            while row := self.sort_model.get_item(n):
                if row.get_item().element is element:
                    if expand:
                        row.set_expanded(True)
                    return n
                n += 1

        pos = expand_up_to_element(element)
        if pos is not None:
            self.selection.set_selected(pos)
        return pos


def new_list_item_ui():
    b = translated_ui_string("gaphor.ui", "treeitem.ui")
    return GLib.Bytes.new(b.encode("utf-8"))


def visible(element):
    return isinstance(
        element, (UML.Relationship, UML.NamedElement, Diagram)
    ) and not isinstance(
        element, (UML.InstanceSpecification, UML.OccurrenceSpecification)
    )


def list_item_factory_setup(_factory, list_item):
    builder = Gtk.Builder()
    builder.set_current_object(list_item)
    builder.extend_with_template(
        list_item,
        type(list_item).__gtype__,
        translated_ui_string("gaphor.ui", "treeitem.ui"),
        -1,
    )
    row = builder.get_object("draggable")
    drag_source = Gtk.DragSource.new()
    drag_source.connect("prepare", list_item_drag_prepare, list_item)
    row.add_controller(drag_source)


def list_item_drag_prepare(source: Gtk.DragSource, x: int, y: int, list_item):
    tree_item = list_item.get_item().get_item()
    print("drag prepare", tree_item.element)
    display = Gdk.Display.get_default()
    theme_icon = Gtk.IconTheme.get_for_display(display).lookup_icon(
        tree_item.icon,
        None,
        24,
        1,
        Gtk.TextDirection.NONE,
        Gtk.IconLookupFlags.FORCE_SYMBOLIC,
    )
    source.set_icon(theme_icon, 0, 0)

    v = GObject.Value(GObject.TYPE_STRING)
    v.set_string(f"element:{tree_item.element.id}")
    return Gdk.ContentProvider.new_for_value(v)


def tree_item_sort(a, b, _user_data=None):
    na = GLib.utf8_collate_key(a.text, -1).lower()
    nb = GLib.utf8_collate_key(b.text, -1).lower()
    return (na > nb) - (na < nb)


class TreeModel:
    def __init__(self):
        super().__init__()
        self.branches: dict[TreeItem | None, Gio.ListStore] = {
            None: Gio.ListStore.new(TreeItem.__gtype__)
        }

    @property
    def root(self):
        return self.branches[None]

    def sync(self, element):
        if visible(element) and (tree_item := self.tree_item_for_element(element)):
            tree_item.sync()

    def child_model(self, item: TreeItem, _user_data=None):
        """This method will create branches on demand (lazy)."""
        branches = self.branches
        if item in branches:
            return branches[item]
        elif owned_elements := [
            e
            for e in item.element.ownedElement
            if e.owner is item.element and visible(e)
        ]:
            new_branch = Gio.ListStore.new(TreeItem.__gtype__)
            self.branches[item] = new_branch
            for e in owned_elements:
                new_branch.append(TreeItem(e))
            return new_branch
        return None

    def list_model_for_element(self, element: Element | None) -> Gio.ListStore | None:
        if element is None:
            return self.root
        return next(
            (m for ti, m in self.branches.items() if ti and ti.element is element), None
        )

    def tree_item_for_element(self, element: Element | None) -> TreeItem | None:
        if element is None:
            return None
        owner = element.owner
        if owner_model := self.list_model_for_element(owner):
            return next((ti for ti in owner_model if ti.element is element), None)
        return None

    def add_element(self, element: Element) -> None:
        if (not visible(element)) or self.tree_item_for_element(element):
            return

        if (owner_model := self.list_model_for_element(element.owner)) is not None:
            owner_model.append(TreeItem(element))
        elif owner_tree_item := self.tree_item_for_element(element.owner):
            self.notify_child_model(owner_tree_item)

    def remove_element(self, element: Element, owner=no_owner) -> None:
        for child in element.ownedElement:
            self.remove_element(child)

        if (
            owner_model := self.list_model_for_element(
                element.owner if owner is no_owner else owner
            )
        ) is not None:
            index = next(
                (i for i, ti in enumerate(owner_model) if ti.element is element), None
            )
            if index is not None:
                owner_model.remove(index)
            if not len(owner_model):
                self.remove_branch(owner_model)

    def remove_branch(self, branch: Gio.ListStore) -> None:
        tree_item = next(ti for ti, b in self.branches.items() if b is branch)
        if tree_item is None:
            # Do never remove the root branch
            return

        del self.branches[tree_item]
        self.notify_child_model(tree_item)

    def notify_child_model(self, tree_item):
        # Only notify the change, the branch is created in child_model()
        owner_tree_item = self.tree_item_for_element(tree_item.element.owner)
        if (owner_model := self.branches.get(owner_tree_item)) is not None:
            found, index = owner_model.find(tree_item)
            if found:
                owner_model.items_changed(index, 1, 1)

    def clear(self) -> None:
        root = self.root
        root.remove_all()
        self.branches.clear()
        self.branches[None] = root


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
        self.relationships_item = TreeItem(None)
        self.relationships_item.text = gettext("<Relationships>")

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

    def do_get_item(self, position) -> TreeItem:
        if position == 0 and self.has_relationships:
            return self.relationships_item
        return self.others.get_item(position - self.has_relationships)  # type: ignore[no-any-return]


def uml_relationship_matcher(item):
    return isinstance(item, TreeItem) and isinstance(item.element, UML.Relationship)


def negating_matcher(matcher):
    return lambda item: not matcher(item)
