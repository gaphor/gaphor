from __future__ import annotations

from unicodedata import normalize

from gi.repository import Gio, GObject, Pango

from gaphor import UML
from gaphor.core.format import format
from gaphor.core.modeling import Diagram, Element
from gaphor.diagram.iconname import get_icon_name
from gaphor.i18n import gettext

_no_value = object()


class TreeItem(GObject.Object):
    def __init__(self, element: Element | None):
        super().__init__()
        self.element = element
        if element:
            self.sync()

    text = GObject.Property(type=str)
    icon = GObject.Property(type=str)
    icon_visible = GObject.Property(type=bool, default=False)
    attributes = GObject.Property(type=Pango.AttrList)
    visible_child_name = GObject.Property(type=str, default="default")

    @GObject.Property(type=str)
    def read_only(self):
        return not self.element or not hasattr(self.element, "name")

    @GObject.Property(type=str)
    def edit_text(self):
        return "" if self.read_only else (self.element.name or "")

    @edit_text.setter  # type: ignore[no-redef]
    def edit_text(self, text):
        if not self.read_only:
            self.element.name = text or ""

    def sync(self) -> None:
        if element := self.element:
            self.text = format(element) or gettext("<None>")
            self.notify("edit-text")
            self.icon = get_icon_name(element)
            self.icon_visible = bool(
                self.icon
                and not isinstance(
                    element, (UML.Parameter, UML.Property, UML.Operation)
                )
            )
            self.attributes = pango_attributes(element)

    def start_editing(self):
        self.visible_child_name = "editing"


class RelationshipItem(TreeItem):
    def __init__(self, child_model):
        super().__init__(None)
        self.child_model = child_model
        self.text = gettext("<Relationships>")

    def start_editing(self):
        pass


class Branch:
    def __init__(self):
        self.elements = Gio.ListStore.new(TreeItem.__gtype__)
        self.relationships = Gio.ListStore.new(TreeItem.__gtype__)

    def append(self, element: Element):
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

    def changed(self, element: Element):
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


def visible(element):
    return isinstance(
        element, (UML.Relationship, UML.NamedElement, Diagram)
    ) and not isinstance(
        element, (UML.InstanceSpecification, UML.OccurrenceSpecification)
    )


def tree_item_sort(a, b, _user_data=None):
    if isinstance(a, RelationshipItem):
        return -1
    if isinstance(b, RelationshipItem):
        return 1
    na = normalize("NFC", a.text).casefold()
    nb = normalize("NFC", b.text).casefold()
    return (na > nb) - (na < nb)


class TreeModel:
    def __init__(self):
        super().__init__()
        self.branches: dict[TreeItem | None, Branch] = {None: Branch()}

    @property
    def root(self) -> Gio.ListStore:
        return self.branches[None].elements

    def sync(self, element):
        if visible(element) and (tree_item := self.tree_item_for_element(element)):
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
        elif owned_elements := [
            e
            for e in item.element.ownedElement
            if e.owner is item.element and visible(e)
        ]:
            new_branch = Branch()
            self.branches[item] = new_branch
            for e in owned_elements:
                new_branch.append(e)
            return new_branch.elements
        return None

    def owner_branch_for_element(
        self, element: Element, former_owner=_no_value
    ) -> Branch | None:
        if (
            owner := element.owner if former_owner is _no_value else former_owner
        ) is None:
            return self.branches[None]

        return next(
            (m for ti, m in self.branches.items() if ti and ti.element is owner),
            None,
        )

    def tree_item_for_element(self, element: Element | None) -> TreeItem | None:
        if element is None:
            return None
        if owner_branch := self.owner_branch_for_element(element):
            return next((ti for ti in owner_branch if ti.element is element), None)
        return None

    def add_element(self, element: Element) -> None:
        if (not visible(element)) or self.tree_item_for_element(element):
            return

        if (owner_branch := self.owner_branch_for_element(element)) is not None:
            owner_branch.append(element)
        elif element.owner:
            self.notify_child_model(element.owner)

    def remove_element(self, element: Element, former_owner=_no_value) -> None:
        for child in element.ownedElement:
            self.remove_element(child)

        if (
            owner_branch := self.owner_branch_for_element(
                element, former_owner=former_owner
            )
        ) is not None:
            owner_branch.remove(element)

            if not len(owner_branch):
                self.remove_branch(owner_branch)

    def remove_branch(self, branch: Branch) -> None:
        tree_item = next(ti for ti, b in self.branches.items() if b is branch)
        if tree_item is None:
            # Do never remove the root branch
            return

        del self.branches[tree_item]

        self.notify_child_model(tree_item.element)

    def notify_child_model(self, element):
        # Only notify the change, the branch is created in child_model()
        owner_tree_item = self.tree_item_for_element(element.owner)
        if (owner_branch := self.branches.get(owner_tree_item)) is not None:
            owner_branch.changed(element)

    def clear(self) -> None:
        root = self.branches[None]
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
