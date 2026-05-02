import importlib.resources
from unicodedata import normalize

from gi.repository import Gio, GObject, Pango

from gaphor.core import event_handler
from gaphor.core.format import format
from gaphor.core.modeling import (
    Base,
    DerivedAdded,
    DerivedDeleted,
    DerivedSet,
    ElementCreated,
    ElementDeleted,
    ElementUpdated,
    ModelFlushed,
    ModelReady,
)
from gaphor.diagram.group import Root, RootType, owner, owns
from gaphor.diagram.iconname import icon_name
from gaphor.KerML import kerml


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
        element = self.element
        if not element:
            return ""
        return (
            getattr(element, "declaredName", None)
            or getattr(element, "elementId", None)
            or ""
        )

    @editable_text.setter  # type: ignore[no-redef]
    def editable_text(self, text):
        if element := self.element:
            if hasattr(element, "declaredName"):
                element.declaredName = text or ""

    def sync(self) -> None:
        if element := self.element:
            self.readonly_text = format(element)
            self.notify("editable-text")
            self.icon = icon_name(element)
            self.icon_visible = bool(self.icon)
            self.attributes = Pango.AttrList()

    def start_editing(self):
        self.editing = True


class Branch:
    def __init__(self):
        self.elements = Gio.ListStore.new(TreeItem.__gtype__)

    def append(self, element: Base):
        self.elements.append(TreeItem(element))

    def remove(self, element: Base):
        if (
            index := next(
                (i for i, ti in enumerate(self.elements) if ti.element is element),
                None,
            )
        ) is not None:
            self.elements.remove(index)

    def remove_all(self):
        self.elements.remove_all()

    def changed(self, element: Base):
        if not (
            tree_item := next(
                (ti for ti in self.elements if ti.element is element), None
            )
        ):
            return
        found, index = self.elements.find(tree_item)
        if found:
            self.elements.items_changed(index, 1, 1)

    def __len__(self):
        return self.elements.get_n_items()

    def __iter__(self):
        yield from self.elements


def tree_item_sort(a: TreeItem, b: TreeItem) -> int:
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
    def root(self) -> Gio.ListStore:
        return self.branches[Root].elements

    @property
    def template(self) -> str:
        return (importlib.resources.files("gaphor.SysML2") / "treeitem.ui").read_text(
            encoding="utf-8"
        )

    def child_model(self, item: TreeItem) -> Gio.ListStore | None:
        branches = self.branches
        if item in branches:
            return branches[item].elements
        if not item.element:
            return None
        if owned_elements := owns(item.element):
            new_branch = Branch()
            self.branches[item] = new_branch
            for element in owned_elements:
                new_branch.append(element)
            return new_branch.elements
        return None

    def tree_item_sort(self, a, b) -> int:
        return tree_item_sort(a, b)

    def should_expand(self, item: TreeItem, element: Base) -> bool:
        return False

    def owner_branch_for_element(self, element: Base) -> Branch | None:
        if (own := owner(element)) is Root:
            return self.branches[Root]

        return next(
            (
                branch
                for tree_item, branch in self.branches.items()
                if isinstance(tree_item, TreeItem) and tree_item.element is own
            ),
            None,
        )

    def tree_item_for_element(self, element: Base | RootType) -> TreeItem | None:
        if element is Root:
            return None
        if (owner_branch := self.owner_branch_for_element(element)) is not None:
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
        for child in owns(element):
            self.remove_element(child)

        for owner_branch in [
            branch
            for branch in self.branches.values()
            if element in (i.element for i in branch)
        ]:
            owner_branch.remove(element)

            if not len(owner_branch):
                self.remove_branch(owner_branch)

    def remove_branch(self, branch: Branch) -> None:
        tree_item = next(
            tree_item for tree_item, b in self.branches.items() if b is branch
        )
        if tree_item is Root:
            return

        del self.branches[tree_item]

        if tree_item.element:
            self.notify_child_model(tree_item.element)

    def notify_child_model(self, element: Base):
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
        if event.property in (kerml.Element.ownedElement,):
            self.notify_child_model(event.element)

    @event_handler(DerivedSet)
    def on_owner_changed(self, event: DerivedSet):
        if event.property in (kerml.Element.owner,) and owner(event.element):
            element = event.element
            self.remove_element(element)
            self.add_element(element)
            if self._on_select:
                self._on_select(element)

    @event_handler(ElementUpdated)
    def on_attribute_changed(self, event: ElementUpdated):
        if tree_item := self.tree_item_for_element(event.element):
            tree_item.sync()
            if self._on_sync:
                self._on_sync()

    @event_handler(ModelReady, ModelFlushed)
    def on_model_ready(self, _event=None):
        self.clear()
        for element in self.element_factory.select(owner):
            self.add_element(element)
