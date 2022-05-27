import pytest
from gi.repository import Gtk

from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.ui.treemodel import TreeComponent, TreeItem, TreeModel

GTK3 = Gtk.get_major_version() == 3


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


def test_tree_model():
    tree_model = TreeModel(owner=None)

    assert tree_model.get_n_items() == 0
    assert tree_model.get_item(0) is None


@pytest.mark.skipif(GTK3, reason="GTK 4+ only")
def test_tree_component_add_element(tree_component, element_factory):
    tree_model = tree_component.model
    items_changed = ItemChangedHandler()
    tree_model.connect("items-changed", items_changed)

    element = element_factory.create(UML.Class)

    assert tree_model.get_n_items() == 1
    assert tree_model.get_item(0).element is element
    assert items_changed.added == 1


@pytest.mark.skipif(GTK3, reason="GTK 4+ only")
def test_tree_component_remove_element(tree_component, element_factory):
    tree_model = tree_component.model
    element = element_factory.create(UML.Class)
    items_changed = ItemChangedHandler()
    tree_model.connect("items-changed", items_changed)

    element.unlink()

    assert tree_model.get_n_items() == 0
    assert items_changed.removed == 1


@pytest.mark.skipif(GTK3, reason="GTK 4+ only")
def test_tree_subtree_changed(tree_component, element_factory):
    tree_model = tree_component.model
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)
    items_changed = ItemChangedHandler()
    tree_model.connect("items-changed", items_changed)

    class_.package = package

    assert tree_model.get_n_items() == 1
    assert items_changed.added == 1
    assert items_changed.removed == 2


@pytest.mark.skipif(GTK3, reason="GTK 4+ only")
def test_tree_component_add_nested_element(tree_component, element_factory):
    tree_model = tree_component.model
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package
    child_model = tree_component.tree_model_for_element(package)

    assert tree_model.tree_item_for_element(package)
    assert tree_model.tree_item_for_element(package).child_model
    assert child_model.tree_item_for_element(class_)


@pytest.mark.skipif(GTK3, reason="GTK 4+ only")
def test_tree_component_unset_nested_element(tree_component, element_factory):
    tree_model = tree_component.model
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package
    del class_.package

    child_model = tree_component.tree_model_for_element(package)
    assert tree_model.tree_item_for_element(package)
    assert tree_model.tree_item_for_element(class_)
    assert not child_model.tree_item_for_element(class_)


@pytest.mark.skipif(GTK3, reason="GTK 4+ only")
def test_tree_component_remove_nested_element(tree_component, element_factory):
    tree_model = tree_component.model
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package
    class_.unlink()

    child_model = tree_component.tree_model_for_element(package)
    assert tree_model.tree_item_for_element(package)
    assert child_model.get_n_items() == 0, [i.element for i in child_model.items]


@pytest.mark.skipif(GTK3, reason="GTK 4+ only")
def test_element_name_changed(tree_component, element_factory):
    class_ = element_factory.create(UML.Class)
    tree_item = tree_component.model.tree_item_for_element(class_)

    class_.name = "foo"
    weight, style = tree_item.attributes.get_attributes()

    assert tree_item.text == "foo"
    assert weight.as_int().value == 400
    assert style.as_int().value == 0


@pytest.mark.skipif(GTK3, reason="GTK 4+ only")
def test_element_weight_changed(tree_component, element_factory):
    diagram = element_factory.create(Diagram)
    tree_item = tree_component.model.tree_item_for_element(diagram)
    weight, style = tree_item.attributes.get_attributes()

    assert weight.as_int().value == 700
    assert style.as_int().value == 0


@pytest.mark.skipif(GTK3, reason="GTK 4+ only")
def test_element_style_changed(tree_component, element_factory):
    class_ = element_factory.create(UML.Class)
    tree_item = tree_component.model.tree_item_for_element(class_)

    class_.isAbstract = True
    weight, style = tree_item.attributes.get_attributes()

    assert weight.as_int().value == 400
    assert style.as_int().value == 2


@pytest.mark.skipif(GTK3, reason="GTK 4+ only")
def test_tree_component_model_ready(event_manager, element_factory):
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)
    tree_component = TreeComponent(event_manager, element_factory)
    tree_component.open()

    element_factory.model_ready()

    tree_model = tree_component.model
    class_.package = package
    child_model = tree_component.tree_model_for_element(package)

    assert tree_model.tree_item_for_element(package)
    assert child_model.tree_item_for_element(class_)

    tree_component.close()


# Test: delete nested element in tree component
# Formatting: diagrams bold, abstract elements italic
# Test: name change in (nested) element
# Test: relationships in separate subtree
