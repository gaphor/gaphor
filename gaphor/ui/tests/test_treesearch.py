import pytest

from gaphor import UML
from gaphor.ui.treemodel import TreeModel
from gaphor.ui.treesearch import search, sorted_tree_walker


@pytest.fixture
def tree_model():
    return TreeModel()


@pytest.fixture
def create(element_factory, tree_model):
    def _create(name, parent=None):
        klass = element_factory.create(UML.Class)
        klass.name = name
        if parent:
            klass.nestingClass = parent
        tree_model.add_element(klass)
        return klass

    return _create


def test_search(tree_model, create):
    create("aaa")
    bbb = create("bbb")

    found = search("b", sorted_tree_walker(tree_model))

    assert found.element is bbb


def test_search_no_hit(tree_model, create):
    create("aaa")
    create("bbb")

    found = search("z", sorted_tree_walker(tree_model))

    assert found is None


def test_search_with_child_models(tree_model, create):
    aaa = create("aaa")
    bbb = create("bbb", parent=aaa)

    found = search("b", sorted_tree_walker(tree_model))

    assert found.element is bbb


def test_search_with_start_tree_item(tree_model, create):
    create("aab")
    abb = create("abb")
    bbb = create("bbb")

    found = search(
        "b",
        sorted_tree_walker(
            tree_model, start_tree_item=tree_model.tree_item_for_element(abb)
        ),
    )

    assert found.element is bbb


def test_search_from_current_with_start_tree_item(tree_model, create):
    create("aab")
    abb = create("abb")
    create("bbb")

    found = search(
        "b",
        sorted_tree_walker(
            tree_model,
            start_tree_item=tree_model.tree_item_for_element(abb),
            from_current=True,
        ),
    )

    assert found.element is abb
