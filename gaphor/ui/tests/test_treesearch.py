import pytest

from gaphor import UML
from gaphor.ui.treemodel import TreeModel
from gaphor.ui.treesearch import search


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

    s = search(tree_model, "b")

    assert next(s).element is bbb


def test_search_no_hit(tree_model, create):
    create("aaa")
    create("bbb")

    s = search(tree_model, "z")

    with pytest.raises(StopIteration):
        next(s)


def test_search_with_child_models(tree_model, create):
    aaa = create("aaa")
    bbb = create("bbb", parent=aaa)

    s = search(tree_model, "b")

    assert next(s).element is bbb


def test_update_search_text(tree_model, create):
    create("aaa")
    bbb = create("bbb")
    create("ccc")
    ddd = create("ddd")

    s = search(tree_model, "b")

    assert next(s).element is bbb
    assert s.send("d").element is ddd


def test_search_with_start_tree_item(tree_model, create):
    create("aaa")
    aab = create("aab")
    abb = create("abb")
    bbb = create("bbb")

    s = search(tree_model, "b", start_tree_item=tree_model.tree_item_for_element(abb))

    assert next(s).element is bbb
    assert next(s).element is aab


def test_search_cycles(tree_model, create):
    create("aaa")
    aba = create("aba")
    bbb = create("bbb")

    s = search(tree_model, "b")

    assert next(s).element is aba
    assert next(s).element is bbb
    assert next(s).element is aba


def test_update_search_start_item(tree_model, create):
    create("aaa")
    aab = create("aab")
    abb = create("abb")
    bbb = create("bbb")

    s = search(tree_model, "b")

    assert next(s).element is aab
    assert s.send(tree_model.tree_item_for_element(abb)).element is bbb
