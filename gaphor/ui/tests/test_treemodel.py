import pytest

from gaphor import UML
from gaphor.ui.treemodel import TreeComponent, TreeItem, TreeModel


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


def test_tree_model(element_factory):
    tree_model = TreeModel(element_factory, owner=None)

    assert tree_model.get_n_items() == 0
    assert tree_model.get_item(0) is None


def test_tree_model_with_element(element_factory):
    element = element_factory.create(UML.Class)
    tree_model = TreeModel(element_factory, owner=None)

    assert tree_model.get_n_items() == 1
    assert tree_model.get_item(0).element is element


def test_tree_component_add_element(tree_component, element_factory):
    tree_model = tree_component.model
    items_changed = ItemChangedHandler()
    tree_model.connect("items-changed", items_changed)

    element = element_factory.create(UML.Class)

    assert tree_model.get_n_items() == 1
    assert tree_model.get_item(0).element is element
    assert items_changed.added == 1


def test_tree_component_remove_element(tree_component, element_factory):
    tree_model = tree_component.model
    element = element_factory.create(UML.Class)
    items_changed = ItemChangedHandler()
    tree_model.connect("items-changed", items_changed)

    element.unlink()

    assert tree_model.get_n_items() == 0
    assert items_changed.removed == 1


# Test: delete element in tree component
# Test: create nested element in tree component
# Test: delete nested element in tree component
# Test: ownership changes
# Formatting: diagrams bold, abstract elements italic
# Test: name change in (nested) element
# Test: relationships in separate subtree
