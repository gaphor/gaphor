from __future__ import annotations

import importlib.resources
from unicodedata import normalize

from gi.repository import Gio, GObject, Pango

import gaphor.UML.uml as UML
from gaphor.core import event_handler
from gaphor.core.format import format
from gaphor.core.modeling import (
    Base,
    DerivedAdded,
    DerivedDeleted,
    DerivedSet,
    Diagram,
    ElementCreated,
    ElementDeleted,
    ElementUpdated,
    ModelFlushed,
    ModelReady,
)
from gaphor.diagram.group import Root, RootType, owner, owns
from gaphor.diagram.iconname import icon_name
from gaphor.i18n import gettext


class TreeItem(GObject.Object):
    def __init__(self, element: Base | None):
        super().__init__()
        self.element = element
        self.sync()

    icon = GObject.Property(type=str)
    icon_visible = GObject.Property(type=bool, default=False)

    readonly_text = GObject.Property(type=str)
    attributes = GObject.Property(type=Pango.AttrList)
    editing = GObject.Property(type=bool, default=False)
    can_edit = GObject.Property(type=bool, default=True)

    @GObject.Property(type=str)
    def editable_text(self):
        return (
            (self.element.name or "")
            if isinstance(self.element, UML.NamedElement)
            else ""
        )

    @editable_text.setter  # type: ignore[no-redef]
    def editable_text(self, text):
        if isinstance(self.element, UML.NamedElement):
            self.element.name = text or ""

    def sync(self) -> None:
        if element := self.element:
            self.readonly_text = format(element) or gettext("<None>")
            self.notify("editable-text")
            self.icon = icon_name(element)
            self.icon_visible = bool(
                self.icon
                and not isinstance(
                    element, UML.Parameter | UML.Property | UML.Operation
                )
            )
            self.attributes = pango_attributes(element)

    def start_editing(self):
        self.editing = True


class RelationshipItem(TreeItem):
    def __init__(self, child_model):
        super().__init__(None)
        self.child_model = child_model
        self.readonly_text = gettext("<Relationships>")
        self.can_edit = False


class Branch:
    def __init__(self):
        self.elements = Gio.ListStore.new(TreeItem.__gtype__)
        self.relationships = Gio.ListStore.new(TreeItem.__gtype__)

    def append(self, element: Base):
        if isinstance(element, UML.Relationship):
            if self.relationships.get_n_items() == 0:
                self.elements.insert(0, RelationshipItem(self.relationships))
            self.relationships.append(TreeItem(element))
        else:
            self.elements.append(TreeItem(element))

    def remove(self, element):
        list_store = (
            self.relationships
            if isinstance(element, UML.Relationship)
            else self.elements
        )
        if (
            index := next(
                (i for i, ti in enumerate(list_store) if ti.element is element),
                None,
            )
        ) is not None:
            list_store.remove(index)

        # Clean up empty relationships node
        if list_store is self.relationships and self.relationships.get_n_items() == 0:
            for i, e in enumerate(self.elements):
                if isinstance(e, RelationshipItem):
                    self.elements.remove(i)
                    break

    def remove_all(self):
        self.relationships.remove_all()
        self.elements.remove_all()

    def changed(self, element: Base):
        list_store = (
            self.relationships
            if isinstance(element, UML.Relationship)
            else self.elements
        )
        if not (
            tree_item := next((ti for ti in list_store if ti.element is element), None)
        ):
            return
        found, index = list_store.find(tree_item)
        if found:
            list_store.items_changed(index, 1, 1)

    def __len__(self):
        return self.elements.get_n_items()

    def __getitem__(self, index):
        return self.elements.get_item(index)

    def __iter__(self):
        yield from self.elements
        yield from self.relationships


def tree_item_sort(a: TreeItem, b: TreeItem) -> int:
    if isinstance(a, RelationshipItem):
        return -1
    if isinstance(b, RelationshipItem):
        return 1
    na = normalize("NFC", a.readonly_text).casefold()
    nb = normalize("NFC", b.readonly_text).casefold()
    return (na > nb) - (na < nb)


class TreeModel:
    def __init__(self, event_manager, element_factory, on_select=None, on_sync=None):
        super().__init__()
        self.branches: dict[TreeItem | RootType, Branch] = {Root: Branch()}
        self._on_select = on_select
        self._on_sync = on_sync
        self.event_manager = event_manager
        self.element_factory = element_factory

        event_manager.subscribe(self.on_element_created)
        event_manager.subscribe(self.on_element_deleted)
        event_manager.subscribe(self.on_owner_changed)
        event_manager.subscribe(self.on_owned_element_changed)
        event_manager.subscribe(self.on_attribute_changed)
        event_manager.subscribe(self.on_model_ready)

        self.on_model_ready()

    def shutdown(self) -> None:
        self.event_manager.unsubscribe(self.on_element_created)
        self.event_manager.unsubscribe(self.on_element_deleted)
        self.event_manager.unsubscribe(self.on_owner_changed)
        self.event_manager.unsubscribe(self.on_owned_element_changed)
        self.event_manager.unsubscribe(self.on_attribute_changed)
        self.event_manager.unsubscribe(self.on_model_ready)

    @property
    def template(self) -> str:
        return (importlib.resources.files("gaphor.UML") / "treeitem.ui").read_text(
            encoding="utf-8"
        )

    @property
    def root(self) -> Gio.ListStore:
        return self.branches[Root].elements

    def sync(self, element, seen=None):
        if seen is None:
            seen = set()

        if (
            element in seen
            or not owner(element)
            or not (tree_item := self.tree_item_for_element(element))
        ):
            return

        seen.add(element)
        tree_item.sync()
        if self._on_sync:
            self._on_sync()

        if own := owner(element):
            self.sync(own, seen)

        if isinstance(element, UML.Parameter) and element.activityParameterNode:
            for node in element.activityParameterNode:
                self.sync(node, seen)

        if isinstance(element, UML.Type):
            for e in self.element_factory.select(UML.TypedElement):
                if e.type is element:
                    self.sync(e, seen)

    def child_model(self, item: TreeItem) -> Gio.ListStore | None:
        """This method will create branches on demand (lazy)."""
        branches = self.branches
        if item in branches:
            return branches[item].elements
        elif isinstance(item, RelationshipItem):
            return item.child_model
        elif not item.element:
            return None
        elif owned_elements := owns(item.element):
            new_branch = Branch()
            self.branches[item] = new_branch
            for e in owned_elements:
                new_branch.append(e)
            return new_branch.elements
        return None

    def tree_item_sort(self, a, b) -> int:
        return tree_item_sort(a, b)

    def should_expand(self, item: TreeItem, element: Base) -> bool:
        return isinstance(element, UML.Relationship) and isinstance(
            item, RelationshipItem
        )

    def owner_branch_for_element(self, element: Base) -> Branch | None:
        if (own := owner(element)) is Root:
            return self.branches[Root]

        return next(
            (
                m
                for ti, m in self.branches.items()
                if isinstance(ti, TreeItem) and ti.element is own
            ),
            None,
        )

    def tree_item_for_element(self, element: Base | RootType) -> TreeItem | None:
        if element is Root:
            return None
        if owner_branch := self.owner_branch_for_element(element):
            return next((ti for ti in owner_branch if ti.element is element), None)
        return None

    def add_element(self, element: Base) -> None:
        if (not owner(element)) or self.tree_item_for_element(element):
            return

        if (owner_branch := self.owner_branch_for_element(element)) is not None:
            owner_branch.append(element)
        elif isinstance((own := owner(element)), Base):
            self.notify_child_model(own)

    def remove_element(self, element: Base) -> None:
        if not isinstance(element, Base):
            return

        for child in owns(element):
            self.remove_element(child)

        for owner_branch in [
            b for b in self.branches.values() if element in (i.element for i in b)
        ]:
            owner_branch.remove(element)

            if not len(owner_branch):
                self.remove_branch(owner_branch)

    def remove_branch(self, branch: Branch) -> None:
        tree_item = next(ti for ti, b in self.branches.items() if b is branch)
        if tree_item is Root:
            # Do never remove the root branch
            return

        del self.branches[tree_item]

        if tree_item.element:
            self.notify_child_model(tree_item.element)

    def notify_child_model(self, element: Base):
        # Only notify the change, the branch is created in child_model()
        if not self.branches.get(self.tree_item_for_element(element) or Root) and (
            owner_branch := self.branches.get(
                self.tree_item_for_element(owner(element) or Root) or Root
            )
        ):
            owner_branch.changed(element)

    def clear(self) -> None:
        root = self.branches[Root]
        root.remove_all()
        self.branches.clear()
        self.branches[Root] = root

    @event_handler(ElementCreated)
    def on_element_created(self, event: ElementCreated):
        self.add_element(event.element)

    @event_handler(ElementDeleted)
    def on_element_deleted(self, event: ElementDeleted):
        self.remove_element(event.element)

    @event_handler(DerivedAdded, DerivedDeleted)
    def on_owned_element_changed(self, event):
        """Ensure we update the node once owned elements change."""
        if event.property in (UML.Element.ownedElement, UML.Namespace.member):
            self.notify_child_model(event.element)

    @event_handler(DerivedSet)
    def on_owner_changed(self, event: DerivedSet):
        # Should check on ownedElement as well, since it may not have been updated
        # before this thing triggers
        if (
            event.property in (UML.Element.owner, UML.NamedElement.memberNamespace)
        ) and owner(event.element):
            element = event.element
            self.remove_element(element)
            self.add_element(element)
            if self._on_select:
                self._on_select(element)

    @event_handler(ElementUpdated)
    def on_attribute_changed(self, event: ElementUpdated):
        self.sync(event.element)

    @event_handler(ModelReady, ModelFlushed)
    def on_model_ready(self, _event=None):
        self.clear()

        for element in self.element_factory.select(owner):
            self.add_element(element)


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
            if isinstance(element, UML.Classifier | UML.BehavioralFeature)
            and element.isAbstract
            else Pango.Style.NORMAL
        )
    )
    return attrs
