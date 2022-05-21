from gaphor import UML
from gaphor.ui.treemodel import TreeItem, TreeModel


def test_tree_item_gtype():
    assert TreeItem.__gtype__.name == "gaphor+ui+treemodel+TreeItem"


def test_tree_model(element_factory):
    tree_model = TreeModel(element_factory, owner=None)

    assert tree_model.get_n_items() == 0
    assert tree_model.get_item(0) is None


def test_tree_model_with_element(element_factory):
    element = element_factory.create(UML.Class)
    tree_model = TreeModel(element_factory, owner=None)

    assert tree_model.get_n_items() == 1, tree_model.items
    assert tree_model.get_item(0).element is element
