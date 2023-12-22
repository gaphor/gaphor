from gaphor import UML
from gaphor.i18n import gettext
from gaphor.ui.treemodel import (
    Branch,
    RelationshipItem,
    TreeItem,
    TreeModel,
    tree_item_sort,
)


class ItemChangedHandler:
    def __init__(self):
        self.added = 0
        self.removed = 0
        self.positions = []

    def __call__(self, _obj, position, removed, added):
        self.positions.append(position)
        self.removed += removed
        self.added += added


def test_tree_item_gtype():
    assert TreeItem.__gtype__.name == "gaphor+ui+treemodel+TreeItem"


def test_branch_add_element(element_factory):
    branch = Branch()
    element = element_factory.create(UML.Class)

    branch.append(element)

    assert len(branch) == 1
    assert branch[0].element is element


def test_branch_remove_element(element_factory):
    branch = Branch()
    element = element_factory.create(UML.Class)
    branch.append(element)

    branch.remove(element)

    assert len(branch) == 0


def test_branch_add_relationship(element_factory):
    branch = Branch()
    element = element_factory.create(UML.Association)

    branch.append(element)

    assert len(branch) == 1
    assert isinstance(branch[0], RelationshipItem)
    assert branch.relationships[0].element is element


def test_tree_model_add_element(element_factory):
    tree_model = TreeModel()
    element = element_factory.create(UML.Class)

    tree_model.add_element(element)
    tree_item = tree_model.tree_item_for_element(element)

    assert tree_item.element is element


def test_tree_model_add_nested_element(element_factory):
    tree_model = TreeModel()
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package
    tree_model.add_element(package)
    tree_model.add_element(class_)
    tree_model.child_model(tree_model.tree_item_for_element(package))
    class_item = tree_model.tree_item_for_element(class_)
    package_item = tree_model.tree_item_for_element(package)

    assert tree_model.branches.get(package_item) is not None
    assert tree_model.branches.get(package_item)[0] is class_item
    assert tree_model.branches.get(class_item) is None


def test_tree_model_add_nested_element_in_reverse_order(element_factory):
    tree_model = TreeModel()
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package
    tree_model.add_element(class_)
    tree_model.add_element(package)
    tree_model.child_model(tree_model.tree_item_for_element(package))
    class_item = tree_model.tree_item_for_element(class_)
    package_item = tree_model.tree_item_for_element(package)

    assert tree_model.branches.get(package_item) is not None
    assert tree_model.branches.get(package_item)[0] is class_item
    assert tree_model.branches.get(class_item) is None


def test_tree_model_remove_element(element_factory):
    tree_model = TreeModel()
    element = element_factory.create(UML.Class)
    tree_model.add_element(element)

    tree_model.remove_element(element)
    tree_item = tree_model.tree_item_for_element(element)

    assert tree_item is None


def test_tree_model_remove_nested_element(element_factory):
    tree_model = TreeModel()
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package
    tree_model.add_element(package)
    tree_model.add_element(class_)
    tree_model.child_model(tree_model.tree_item_for_element(package))
    tree_model.remove_element(class_)

    assert len(tree_model.branches) == 1
    assert None in tree_model.branches
    assert tree_model.tree_item_for_element(package) is not None
    assert tree_model.tree_item_for_element(class_) is None


def test_tree_model_remove_package_with_nested_element(element_factory):
    tree_model = TreeModel()
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package
    tree_model.add_element(package)
    tree_model.add_element(class_)
    tree_model.remove_element(package)

    assert tree_model.tree_item_for_element(package) is None
    assert len(tree_model.branches) == 1
    assert None in tree_model.branches
    assert tree_model.tree_item_for_element(package) is None
    assert tree_model.tree_item_for_element(class_) is None


def test_tree_model_remove_from_different_owner(element_factory):
    tree_model = TreeModel()
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    tree_model.add_element(package)
    tree_model.add_element(class_)
    class_.package = package
    tree_model.remove_element(class_, former_owner=None)

    assert tree_model.tree_item_for_element(package) is not None
    assert len(tree_model.root) == 1


def test_tree_model_change_owner(element_factory):
    tree_model = TreeModel()
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    tree_model.add_element(package)
    tree_model.add_element(class_)
    class_.package = package
    tree_model.remove_element(class_, former_owner=None)
    tree_model.add_element(class_)
    package_item = tree_model.tree_item_for_element(package)
    tree_model.child_model(package_item)
    class_item = tree_model.tree_item_for_element(class_)
    package_model = tree_model.branches[package_item]

    assert package_item in tree_model.root
    assert class_item not in tree_model.root
    assert class_item in package_model


def test_tree_model_relationship_subtree(element_factory):
    tree_model = TreeModel()
    package = element_factory.create(UML.Package)
    association = element_factory.create(UML.Association)
    association.package = package

    tree_model.add_element(package)
    tree_model.add_element(association)
    package_item = tree_model.tree_item_for_element(package)
    tree_model.child_model(package_item)
    association_item = tree_model.tree_item_for_element(association)
    package_model = tree_model.branches[package_item]
    relationship_item = package_model[0]
    branch = tree_model.owner_branch_for_element(association)
    relationship_model = branch.relationships

    assert package_model
    assert isinstance(relationship_item, RelationshipItem)
    assert relationship_item.readonly_text == gettext("<Relationships>")
    assert association_item is relationship_model.get_item(0)


def test_tree_model_second_relationship(element_factory):
    tree_model = TreeModel()
    package = element_factory.create(UML.Package)
    association = element_factory.create(UML.Association)
    association.package = package

    tree_model.add_element(package)
    tree_model.add_element(association)
    package_item = tree_model.tree_item_for_element(package)
    tree_model.child_model(package_item)
    branch = tree_model.owner_branch_for_element(association)
    relationship_model = branch.relationships

    new_association = element_factory.create(UML.Association)
    new_association.package = package
    tree_model.add_element(new_association)

    association_item = tree_model.tree_item_for_element(association)
    new_association_item = tree_model.tree_item_for_element(new_association)

    assert association_item
    assert new_association_item
    assert association_item is relationship_model[0]
    assert new_association_item is relationship_model[1]


def test_tree_model_remove_relationship(element_factory):
    tree_model = TreeModel()
    package = element_factory.create(UML.Package)
    association = element_factory.create(UML.Association)
    association.package = package
    tree_model.add_element(package)
    tree_model.add_element(association)
    package_item = tree_model.tree_item_for_element(package)
    tree_model.child_model(package_item)

    tree_model.remove_element(association)
    package_model = tree_model.branches.get(package_item)

    assert not package_model


def test_tree_model_sort_relationship_item_first(element_factory):
    a = TreeItem(UML.Package())
    a.readonly_text = "a"
    b = TreeItem(UML.Package())
    b.readonly_text = "b"
    r = RelationshipItem(None)

    assert tree_item_sort(r, b) == -1
    assert tree_item_sort(a, r) == 1
    assert tree_item_sort(a, b) == -1
    assert tree_item_sort(b, a) == 1


def test_element_with_member_and_no_owner(element_factory):
    tree_model = TreeModel()
    property = element_factory.create(UML.Property)
    association = element_factory.create(UML.Association)
    association.memberEnd = property
    tree_model.add_element(association)
    tree_model.add_element(property)
    association_item = tree_model.tree_item_for_element(association)
    tree_model.child_model(association_item)
    property_item = tree_model.tree_item_for_element(property)

    association_model = tree_model.branches.get(association_item)

    assert property_item in association_model.elements
