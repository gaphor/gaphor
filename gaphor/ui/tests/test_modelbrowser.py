import pytest

from gaphor import UML
from gaphor.core.modeling import Diagram, ModelReady
from gaphor.i18n import gettext
from gaphor.ui.modelbrowser import (
    ElementDragData,
    ModelBrowser,
    SearchEngine,
    get_first_selected_item,
    list_item_drop_drop,
)
from gaphor.UML import recipes


@pytest.fixture
def model_browser(event_manager, element_factory, modeling_language):
    model_browser = ModelBrowser(event_manager, element_factory, modeling_language)
    model_browser.open()
    yield model_browser
    model_browser.close()


class ItemChangedHandler:
    def __init__(self):
        self.added = 0
        self.removed = 0
        self.positions = []

    def __call__(self, _obj, position, removed, added):
        self.positions.append(position)
        self.removed += removed
        self.added += added


def test_show_item_in_tree_list_model(model_browser, element_factory):
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package

    pos = model_browser.select_element(class_)
    tree_model = model_browser.selection

    assert pos == 1
    assert tree_model.get_item(0).get_item().element is package
    assert tree_model.get_item(1).get_item().element is class_


def test_model_browser_remove_element(model_browser, element_factory):
    tree_model = model_browser.model.root
    element = element_factory.create(UML.Class)
    items_changed = ItemChangedHandler()
    tree_model.connect("items-changed", items_changed)

    element.unlink()

    assert len(tree_model) == 0
    assert items_changed.removed == 1


def test_model_browser_add_nested_element(model_browser, element_factory):
    tree_model = model_browser.model
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package
    package_item = tree_model.tree_item_for_element(package)
    child_model = tree_model.child_model(package_item)

    assert package_item in tree_model.root
    assert tree_model.tree_item_for_element(class_) in child_model


def test_model_browser_unset_nested_element(model_browser, element_factory):
    tree_model = model_browser.model
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


def test_model_browser_remove_nested_element(model_browser, element_factory):
    tree_model = model_browser.model
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)

    class_.package = package
    package_item = tree_model.tree_item_for_element(package)
    assert tree_model.child_model(package_item)

    class_.unlink()

    child_model = tree_model.child_model(package_item)
    assert tree_model.tree_item_for_element(package) is not None
    assert child_model is None


def test_change_from_member_to_owner(model_browser, element_factory):
    tree_model = model_browser.model
    property = element_factory.create(UML.Property)
    association = element_factory.create(UML.Association)
    klass = element_factory.create(UML.Class)

    association.memberEnd = property
    klass.ownedAttribute = property

    association_item = tree_model.tree_item_for_element(association)
    klass_item = tree_model.tree_item_for_element(klass)
    property_item = tree_model.tree_item_for_element(property)
    association_model = tree_model.branches.get(association_item)
    klass_model = tree_model.branches.get(klass_item)

    assert not association_model
    assert property_item in klass_model.elements


def test_element_name_changed(model_browser, element_factory):
    class_ = element_factory.create(UML.Class)
    tree_item = model_browser.model.tree_item_for_element(class_)

    class_.name = "foo"

    weight, style = tree_item.attributes.get_attributes()

    assert tree_item.readonly_text == "foo"
    assert weight.as_int().value == 400
    assert style.as_int().value == 0


def test_element_weight_changed(model_browser, element_factory):
    diagram = element_factory.create(Diagram)
    tree_item = model_browser.model.tree_item_for_element(diagram)
    weight, style = tree_item.attributes.get_attributes()

    assert weight.as_int().value == 700
    assert style.as_int().value == 0


def test_element_style_changed(model_browser, element_factory):
    class_ = element_factory.create(UML.Class)
    tree_item = model_browser.model.tree_item_for_element(class_)

    class_.isAbstract = True
    weight, style = tree_item.attributes.get_attributes()

    assert weight.as_int().value == 400
    assert style.as_int().value == 2


def test_model_browser_model_ready(event_manager, element_factory, modeling_language):
    class_ = element_factory.create(UML.Class)
    package = element_factory.create(UML.Package)
    class_.package = package
    model_browser = ModelBrowser(event_manager, element_factory, modeling_language)
    model_browser.open()
    tree_model = model_browser.model

    event_manager.handle(ModelReady(element_factory))

    assert tree_model.tree_item_for_element(package) is not None
    assert tree_model.tree_item_for_element(class_) is None

    model_browser.close()


def test_tree_model_expand_to_relationship(model_browser, element_factory):
    association = element_factory.create(UML.Association)
    package = element_factory.create(UML.Package)
    association.package = package

    pos = model_browser.select_element(association)

    assert pos == 2
    assert model_browser.get_selected_element() is association


def test_create_diagram(model_browser, element_factory):
    model_browser.tree_view_create_diagram("my type")

    diagram = next(element_factory.select(Diagram))

    assert diagram.diagramType == "my type"


def test_create_package(model_browser, element_factory):
    parent = element_factory.create(UML.Package)
    parent.name = "root"
    model_browser.select_element(parent)
    model_browser.tree_view_create_package()

    package = next(p for p in element_factory.select(UML.Package) if p.name != "root")

    assert package
    assert package.owner is parent


def test_create_toplevel_package(model_browser, element_factory):
    model_browser.tree_view_create_package()

    package = next(p for p in element_factory.select(UML.Package) if p.name != "root")

    assert package
    assert package.owner is None


def test_delete_element(model_browser, element_factory):
    klass = element_factory.create(UML.Class)
    model_browser.select_element(klass)
    assert model_browser.get_selected_element() is klass

    model_browser.tree_view_delete()

    assert not element_factory.lselect()


def test_search_next(model_browser, element_factory):
    class_a = element_factory.create(UML.Class)
    class_a.name = "a"
    class_b = element_factory.create(UML.Class)
    class_b.name = "b"

    search_engine = SearchEngine(model_browser.model, model_browser.tree_view)
    model_browser.select_element(class_a)
    assert model_browser.get_selected_element() is class_a

    search_engine.search_next("b")

    assert model_browser.get_selected_element() is class_b


def test_search_text_changed(model_browser, element_factory):
    class_a = element_factory.create(UML.Class)
    class_a.name = "a"
    class_b = element_factory.create(UML.Class)
    class_b.name = "b"

    search_engine = SearchEngine(model_browser.model, model_browser.tree_view)
    model_browser.select_element(class_a)
    assert model_browser.get_selected_element() is class_a

    search_engine.text_changed("b")

    assert model_browser.get_selected_element() is class_b


def test_generalization_text(model_browser, element_factory):
    general = element_factory.create(UML.Class)
    general.name = "General"
    specific = element_factory.create(UML.Class)
    specific.name = "Specific"
    generalization = element_factory.create(UML.Generalization)
    generalization.specific = specific
    generalization.general = general

    model = model_browser.model
    tree_item = model.tree_item_for_element(specific)
    branch = model.branches[tree_item]
    assert tree_item
    assert branch.relationships[0].element is generalization
    assert branch.relationships[0].readonly_text == gettext("general: General")


def test_drop_multiple_elements(model_browser, element_factory, event_manager):
    class_a = element_factory.create(UML.Class)
    class_a.name = "a"
    class_b = element_factory.create(UML.Class)
    class_b.name = "b"
    gen = element_factory.create(UML.Generalization)
    gen.general = class_a
    gen.specific = class_b
    package = element_factory.create(UML.Package)

    model_browser.select_element(package)
    list_item = MockRowItem(get_first_selected_item(model_browser.selection))

    target = MockDropTarget()
    drag_data = ElementDragData(elements=[class_a, class_b])
    list_item_drop_drop(target, drag_data, 0, 10, list_item, event_manager)

    assert class_b.owner is package
    assert class_a.owner is package


def test_unlink_element_should_not_collapse_branch(
    model_browser, element_factory, event_manager
):
    package = element_factory.create(UML.Package)
    package.name = "p"
    class_a = element_factory.create(UML.Class)
    class_a.package = package
    class_a.name = "a"
    class_b = element_factory.create(UML.Class)
    class_b.package = package
    class_b.name = "b"

    row0 = model_browser.selection.get_item(0)
    row0.set_expanded(True)

    class_a.unlink()

    assert row0.get_item().element is package
    assert row0.get_expanded()
    assert model_browser.selection.get_item(1).get_item().element is class_b


def test_multiplicity_element_should_not_end_up_in_root(model_browser, element_factory):
    port = element_factory.create(UML.Port)
    prop = element_factory.create(UML.Property)
    connector = UML.recipes.create_connector(port, prop)

    model_browser.on_model_ready()
    model = model_browser.model

    assert model.tree_item_for_element(connector.end[0]) is None


def test_stereotype_base_class_should_not_end_up_in_root(
    model_browser, element_factory
):
    profile = element_factory.create(UML.Profile)
    profile.name = "profile"
    metaclass = element_factory.create(UML.Class)
    metaclass.package = profile
    metaclass.name = "Metaclass"
    stereotype = element_factory.create(UML.Stereotype)
    stereotype.package = profile
    stereotype.name = "Stereotype"

    relation = recipes.create_extension(metaclass, stereotype)
    relation.package = profile

    row0 = model_browser.selection.get_item(0)
    assert row0.get_item().element is profile  # not property


def test_drag_and_drop_parent_on_child(model_browser, element_factory, event_manager):
    root = element_factory.create(UML.Package)
    parent = element_factory.create(UML.Package)
    parent.package = root
    parent_diagram = element_factory.create(Diagram)
    parent_diagram.element = parent
    child = element_factory.create(UML.Package)
    child.package = parent
    child_diagram = element_factory.create(Diagram)
    child_diagram.element = child

    model_browser.select_element(parent)
    list_item = MockRowItem(get_first_selected_item(model_browser.selection))

    target = MockDropTarget()
    drag_data = ElementDragData(elements=[parent])
    list_item_drop_drop(target, drag_data, 0, 10, list_item, event_manager)

    assert model_browser.select_element(child) is not None
    assert child.owner is parent
    assert parent.owner is root


class MockRowItem:
    def __init__(self, list_item):
        self.list_item = list_item

    def get_item(self):
        return self.list_item


class MockDropTarget:
    def get_widget(self):
        class Widget:
            def remove_css_class(self, _):
                pass

        return Widget()
