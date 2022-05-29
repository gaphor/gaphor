import pytest
from gi.repository import Gtk

from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.ui.treemodel import TreeComponent, TreeModel

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


def test_tree_model_gtype():
    assert TreeModel.__gtype__.name == "gaphor+ui+treemodel+TreeModel"


def test_tree_model():
    tree_model = TreeModel(element=None)

    assert tree_model.get_n_items() == 0
    assert tree_model.get_item(0) is None
    assert tree_model.get_property("text") == ""
    assert tree_model.get_property("icon") == ""
    assert tree_model.get_property("attributes") is None


@skip_if_gtk3
def test_tree_component_add_element(tree_component, element_factory):
    tree_model = tree_component.model
    items_changed = ItemChangedHandler()
    tree_model.connect("items-changed", items_changed)

    element = element_factory.create(UML.Class)

    assert tree_model.get_n_items() == 1
    assert tree_model.get_item(0).element is element
    assert items_changed.added == 1


@skip_if_gtk3
def test_tree_component_remove_element(tree_component, element_factory):
    tree_model = tree_component.model
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

    root_model = tree_component.model
    root_model_changed = ItemChangedHandler()
    root_model.connect("items-changed", root_model_changed)
    package_model = root_model.tree_model_for_element(package)
    package_model_changed = ItemChangedHandler()
    package_model.connect("items-changed", package_model_changed)

    class_.package = package

    assert root_model.get_n_items() == 1
    assert root_model_changed.added == 1  # add + node changed
    assert root_model_changed.removed == 2
    assert package_model.get_n_items() == 1
    assert package_model_changed.added == 1
    assert package_model_changed.removed == 0


@skip_if_gtk3
def test_tree_component_add_nested_element(tree_component, element_factory):
    tree_model = tree_component.model
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package
    child_model = tree_component.tree_model_for_element(package)

    assert tree_model.tree_model_for_element(package) is not None
    assert tree_model.tree_model_for_element(package).items
    assert child_model.tree_model_for_element(class_) is not None


@skip_if_gtk3
def test_tree_component_unset_nested_element(tree_component, element_factory):
    tree_model = tree_component.model
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package
    del class_.package

    child_model = tree_component.tree_model_for_element(package)
    assert tree_model.tree_model_for_element(package) is not None
    assert tree_model.tree_model_for_element(class_) is not None
    assert not child_model.tree_model_for_element(class_)


@skip_if_gtk3
def test_tree_component_remove_nested_element(tree_component, element_factory):
    tree_model = tree_component.model
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package
    class_.unlink()

    child_model = tree_component.tree_model_for_element(package)
    assert tree_model.tree_model_for_element(package) is not None
    assert child_model.get_n_items() == 0, [i.element for i in child_model.items]


@skip_if_gtk3
def test_element_name_changed(tree_component, element_factory):
    class_ = element_factory.create(UML.Class)
    tree_item = tree_component.model.tree_model_for_element(class_)

    class_.name = "foo"

    print("start tests")
    weight, style = tree_item.attributes.get_attributes()

    assert tree_item.text == "foo"
    assert weight.as_int().value == 400
    assert style.as_int().value == 0


@skip_if_gtk3
def test_element_weight_changed(tree_component, element_factory):
    diagram = element_factory.create(Diagram)
    tree_item = tree_component.tree_model_for_element(diagram)
    weight, style = tree_item.attributes.get_attributes()

    assert weight.as_int().value == 700
    assert style.as_int().value == 0


@skip_if_gtk3
def test_element_style_changed(tree_component, element_factory):
    class_ = element_factory.create(UML.Class)
    tree_item = tree_component.tree_model_for_element(class_)

    class_.isAbstract = True
    weight, style = tree_item.attributes.get_attributes()

    assert weight.as_int().value == 400
    assert style.as_int().value == 2


@skip_if_gtk3
def test_tree_component_model_ready(event_manager, element_factory):
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)
    tree_component = TreeComponent(event_manager, element_factory)
    tree_component.open()

    element_factory.model_ready()

    tree_model = tree_component.model
    class_.package = package
    child_model = tree_component.tree_model_for_element(package)

    assert tree_model.tree_model_for_element(package) is not None
    assert child_model.tree_model_for_element(class_) is not None

    tree_component.close()
