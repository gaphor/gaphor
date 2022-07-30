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
    def __init__(self, element):
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
    def __init__(self):
        super().__init__(None)
        self.text = gettext("<Relationships>")

    def start_editing(self):
        pass


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
        elif not item.element:
            return None
        elif owned_elements := [
            e
            for e in item.element.ownedElement
            if e.owner is item.element and visible(e)
        ]:
            new_branch = Gio.ListStore.new(TreeItem.__gtype__)
            self.branches[item] = new_branch
            for e in owned_elements:
                self._maybe_relationships_model(e, new_branch, create=True).append(
                    TreeItem(e)
                )
            return new_branch
        return None

    def _maybe_relationships_model(
        self, element: Element, owner_model: Gio.ListStore, create: bool
    ) -> Gio.ListStore:
        """Return `owner_model`, or the model to hold relationships."""
        if not isinstance(element, UML.Relationship):
            return owner_model

        if isinstance(owner_model.get_item(0), RelationshipItem):
            return self.branches[owner_model.get_item(0)]

        if create:
            relationship_item = RelationshipItem()
            relationship_branch = Gio.ListStore.new(TreeItem.__gtype__)
            self.branches[relationship_item] = relationship_branch
            # Add item after branch, so it is seen as expandable
            owner_model.insert(0, relationship_item)
            return relationship_branch
        return owner_model

    def list_model_for_element(
        self, element: Element, former_owner=_no_value, create=False
    ) -> Gio.ListStore | None:
        if (
            owner := element.owner if former_owner is _no_value else former_owner
        ) is None:
            return self.root

        if (
            owner_model := next(
                (m for ti, m in self.branches.items() if ti and ti.element is owner),
                None,
            )
        ) is not None:
            return self._maybe_relationships_model(element, owner_model, create)

        return None

    def tree_item_for_element(self, element: Element | None) -> TreeItem | None:
        if element is None:
            return None
        if owner_model := self.list_model_for_element(element):
            return next((ti for ti in owner_model if ti.element is element), None)
        return None

    def add_element(self, element: Element) -> None:
        if (not visible(element)) or self.tree_item_for_element(element):
            return

        if (
            owner_model := self.list_model_for_element(element, create=True)
        ) is not None:
            owner_model.append(TreeItem(element))
        elif element.owner:
            self.notify_child_model(element.owner)

    def remove_element(self, element: Element, former_owner=_no_value) -> None:
        for child in element.ownedElement:
            self.remove_element(child)

        if (
            owner_model := self.list_model_for_element(
                element, former_owner=former_owner
            )
        ) is not None:
            index = next(
                (i for i, ti in enumerate(owner_model) if ti.element is element), None
            )
            if index is not None:
                owner_model.remove(index)

            if not len(owner_model):
                self.remove_branch(
                    owner_model,
                    element.owner if former_owner is _no_value else former_owner,
                )
                # TODO: if relationship, remove Relationships node if empty

    def remove_branch(self, branch: Gio.ListStore, owner) -> None:
        tree_item = next(ti for ti, b in self.branches.items() if b is branch)
        if tree_item is None:
            # Do never remove the root branch
            return

        del self.branches[tree_item]

        if tree_item.element:
            self.notify_child_model(tree_item.element)
        elif isinstance(tree_item, RelationshipItem):
            owner_item = self.tree_item_for_element(owner)
            if owner_model := self.branches.get(owner_item):
                if owner_model.get_item(0) is tree_item:
                    owner_model.remove(0)
        else:
            raise NotImplementedError()

    def notify_child_model(self, element):
        # Only notify the change, the branch is created in child_model()
        if not (tree_item := self.tree_item_for_element(element)):
            return
        if self.branches.get(tree_item):
            return
        owner_tree_item = self.tree_item_for_element(element.owner)
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
