from __future__ import annotations

from enum import Enum
from functools import singledispatch
from unicodedata import normalize

from gi.repository import Gio, GObject, Pango

from gaphor import UML
from gaphor.core.format import format
from gaphor.core.modeling import (
    Base,
    Diagram,
    Element,
)
from gaphor.diagram.iconname import icon_name
from gaphor.i18n import gettext


class TreeItem(GObject.Object):
    def __init__(self, element: Base | None):
        super().__init__()
        self.element = element
        if element:
            self.sync()

    icon = GObject.Property(type=str)
    icon_visible = GObject.Property(type=bool, default=False)

    readonly_text = GObject.Property(type=str)
    attributes = GObject.Property(type=Pango.AttrList)
    editing = GObject.Property(type=bool, default=False)
    can_edit = GObject.Property(type=bool, default=True)

    def read_only(self):
        return not self.element

    @GObject.Property(type=str)
    def editable_text(self):
        return "" if self.read_only() else (self.element.name or "")

    @editable_text.setter  # type: ignore[no-redef]
    def editable_text(self, text):
        if not self.read_only():
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


class RootType(Enum):
    Root = 1


Root = RootType.Root


@singledispatch
def owner(_element: Base) -> Base | RootType | None:
    return None


@owner.register
def _(element: Element):
    if not element.owner and isinstance(element, UML.MultiplicityElement):
        return None

    return element.owner or Root


@owner.register
def _(element: UML.NamedElement):
    return element.owner or element.memberNamespace or Root


@owner.register
def _(element: UML.StructuralFeature):
    if not (element.owner or element.memberNamespace):
        return None

    return element.owner or element.memberNamespace


@owner.register
def _(
    _element: UML.Slot
    | UML.Comment
    | UML.InstanceSpecification
    | UML.OccurrenceSpecification,
):
    return None


@singledispatch
def owns(_element: Base) -> list[Base]:
    return []


@owns.register
def _(element: Element):
    return [e for e in element.ownedElement if e.owner is element and owner(e)] + (
        [
            e
            for e in element.member
            if e.memberNamespace is element and not e.owner and owner(e)
        ]
        if isinstance(element, UML.Namespace)
        else []
    )


def tree_item_sort(a, b, _user_data=None):
    if isinstance(a, RelationshipItem):
        return -1
    if isinstance(b, RelationshipItem):
        return 1
    na = normalize("NFC", a.readonly_text).casefold()
    nb = normalize("NFC", b.readonly_text).casefold()
    return (na > nb) - (na < nb)


class TreeModel:
    def __init__(self):
        super().__init__()
        self.branches: dict[TreeItem | RootType, Branch] = {Root: Branch()}

    @property
    def root(self) -> Gio.ListStore:
        return self.branches[Root].elements

    def sync(self, element):
        if owner(element) and (tree_item := self.tree_item_for_element(element)):
            tree_item.sync()

    def child_model(self, item: TreeItem, _user_data=None) -> Gio.ListStore:
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

        if owner_branch := next(
            (b for b in self.branches.values() if element in (i.element for i in b)),
            None,
        ):
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
