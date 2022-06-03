import pytest
from gi.repository import Gtk

from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.ui.treemodel import (
    RelationshipsModel,
    TreeComponent,
    TreeItem,
    TreeModel,
    uml_relationship_matcher,
)

skip_if_gtk3 = pytest.mark.skipif(
    Gtk.get_major_version() == 3, reason="Gtk.ListView is not supported by GTK 3"
)


@pytest.fixture
def tree_component(event_manager, element_factory):
    tree_component = TreeComponent(event_manager, element_factory)
    tree_component.open()
    yield tree_component
    tree_component.close()


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

    assert tree_model.list_model_for_element(package) is not None
    assert tree_model.list_model_for_element(package).get_item(0).element is class_
    assert tree_model.list_model_for_element(class_) is None


def test_tree_model_add_nested_element_in_reverse_order(element_factory):
    tree_model = TreeModel()
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package
    tree_model.add_element(class_)
    tree_model.add_element(package)
    tree_model.child_model(tree_model.tree_item_for_element(package))

    assert tree_model.list_model_for_element(package) is not None
    assert tree_model.list_model_for_element(package).get_item(0).element is class_
    assert tree_model.list_model_for_element(class_) is None


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

    assert tree_model.list_model_for_element(package) is None
    assert tree_model.list_model_for_element(class_) is None
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
    assert tree_model.list_model_for_element(package) is None
    assert tree_model.list_model_for_element(class_) is None
    assert tree_model.tree_item_for_element(package) is None
    assert tree_model.tree_item_for_element(class_) is None


def test_tree_model_remove_from_different_owner(element_factory):
    tree_model = TreeModel()
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    tree_model.add_element(package)
    tree_model.add_element(class_)
    class_.package = package
    tree_model.remove_element(class_, owner=None)

    assert tree_model.tree_item_for_element(package) is not None
    assert tree_model.root.get_n_items() == 1


def test_tree_model_change_owner(element_factory):
    tree_model = TreeModel()
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    tree_model.add_element(package)
    tree_model.add_element(class_)
    class_.package = package
    tree_model.remove_element(class_, owner=None)
    tree_model.add_element(class_)
    package_item = tree_model.tree_item_for_element(package)
    tree_model.child_model(package_item)
    class_item = tree_model.tree_item_for_element(class_)
    package_model = tree_model.list_model_for_element(package)

    assert package_item in tree_model.root
    assert class_item not in tree_model.root
    assert class_item in package_model


@skip_if_gtk3
def test_show_item_in_tree_list_model(tree_component, element_factory):
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package

    pos = tree_component.focus_element(class_)
    tree_model = tree_component.sort_model

    assert pos == 1
    assert tree_model.get_item(0).get_item().element is package
    assert tree_model.get_item(1).get_item().element is class_


@skip_if_gtk3
def test_tree_component_remove_element(tree_component, element_factory):
    tree_model = tree_component.model.root
    element = element_factory.create(UML.Class)
    items_changed = ItemChangedHandler()
    tree_model.connect("items-changed", items_changed)

    element.unlink()

    assert tree_model.get_n_items() == 0
    assert items_changed.removed == 1


@skip_if_gtk3
def test_tree_subtree_changed(tree_component, element_factory):
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    tree_model = tree_component.model
    root_model = tree_model.root
    root_model_changed = ItemChangedHandler()
    root_model.connect("items-changed", root_model_changed)

    class_.package = package

    assert root_model.get_n_items() == 1
    assert root_model_changed.added == 1
    assert root_model_changed.removed == 2  # remove + node changed


@skip_if_gtk3
def test_tree_component_add_nested_element(tree_component, element_factory):
    tree_model = tree_component.model
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package
    package_item = tree_model.tree_item_for_element(package)
    child_model = tree_model.child_model(package_item)

    assert package_item in tree_model.root
    assert tree_model.tree_item_for_element(class_) in child_model


@skip_if_gtk3
def test_tree_component_unset_nested_element(tree_component, element_factory):
    tree_model = tree_component.model
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package
    del class_.package
    package_item = tree_model.tree_item_for_element(package)
    class_item = tree_model.tree_item_for_element(class_)
    child_model = tree_model.child_model(package_item)

    assert package_item is not None
    assert class_item is not None
    assert child_model is None


@skip_if_gtk3
def test_tree_component_remove_nested_element(tree_component, element_factory):
    tree_model = tree_component.model
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package
    package_item = tree_model.tree_item_for_element(package)
    assert tree_model.child_model(package_item)

    class_.unlink()

    child_model = tree_model.child_model(package_item)
    assert tree_model.tree_item_for_element(package) is not None
    assert child_model is None


@skip_if_gtk3
def test_element_name_changed(tree_component, element_factory):
    class_ = element_factory.create(UML.Class)
    tree_item = tree_component.model.tree_item_for_element(class_)

    class_.name = "foo"

    weight, style = tree_item.attributes.get_attributes()

    assert tree_item.text == "foo"
    assert weight.as_int().value == 400
    assert style.as_int().value == 0


@skip_if_gtk3
def test_element_weight_changed(tree_component, element_factory):
    diagram = element_factory.create(Diagram)
    tree_item = tree_component.model.tree_item_for_element(diagram)
    weight, style = tree_item.attributes.get_attributes()

    assert weight.as_int().value == 700
    assert style.as_int().value == 0


@skip_if_gtk3
def test_element_style_changed(tree_component, element_factory):
    class_ = element_factory.create(UML.Class)
    tree_item = tree_component.model.tree_item_for_element(class_)

    class_.isAbstract = True
    weight, style = tree_item.attributes.get_attributes()

    assert weight.as_int().value == 400
    assert style.as_int().value == 2


@skip_if_gtk3
def test_tree_component_model_ready(event_manager, element_factory):
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)
    class_.package = package
    tree_component = TreeComponent(event_manager, element_factory)
    tree_component.open()
    tree_model = tree_component.model

    element_factory.model_ready()

    assert tree_model.tree_item_for_element(package) is not None
    assert tree_model.tree_item_for_element(class_) is None

    tree_component.close()


@skip_if_gtk3
def xtest_filter_relationships(element_factory):
    filter = Gtk.CustomFilter.new(uml_relationship_matcher)

    assert filter.match(TreeModel(element_factory.create(UML.Relationship)))
    assert filter.match(TreeModel(element_factory.create(UML.Association)))
    assert not filter.match(TreeModel(element_factory.create(UML.Class)))


@skip_if_gtk3
def xtest_relationships_model(element_factory):
    tree_model = TreeModel(None)
    class_ = element_factory.create(UML.Class)
    class_.name = "Foo"
    tree_model.add_element(class_)

    relationships_model = RelationshipsModel(tree_model)

    assert relationships_model.get_n_items() == 1
    assert relationships_model.get_item(0).text == "Foo"


@skip_if_gtk3
def xtest_relationships_model_with_relationships(element_factory):
    tree_model = TreeModel(None)
    class_ = element_factory.create(UML.Class)
    class_.name = "Foo"
    association = element_factory.create(UML.Association)
    association.name = "Bar"
    tree_model.add_element(class_)
    tree_model.add_element(association)

    relationships_model = RelationshipsModel(tree_model)

    assert relationships_model.get_n_items() == 2
    assert relationships_model.get_item(0).text == "<Relationships>"
    assert relationships_model.get_item(1).text == "Foo"
    assert relationships_model.get_item(0).child_model.get_n_items() == 1
    assert relationships_model.get_item(0).child_model.get_item(0).text == "Bar"
