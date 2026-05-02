from gaphor.diagram.group import change_owner
from gaphor.KerML import kerml
from gaphor.SysML2 import sysml2
from gaphor.SysML2.treemodel import TreeModel


def test_top_level_element_appears_in_root(event_manager, element_factory):
    tree_model = TreeModel(event_manager, element_factory)
    package = element_factory.create(kerml.Package)

    assert tree_model.tree_item_for_element(package) is not None


def test_reparented_element_appears_under_owner(event_manager, element_factory):
    tree_model = TreeModel(event_manager, element_factory)
    package = element_factory.create(kerml.Package)
    part = element_factory.create(sysml2.PartDefinition)

    assert change_owner(package, part)

    package_item = tree_model.tree_item_for_element(package)
    assert package_item is not None

    children = tree_model.child_model(package_item)
    assert children is not None
    assert any(tree_item.element is part for tree_item in children)


def test_move_between_owners_updates_branches(event_manager, element_factory):
    tree_model = TreeModel(event_manager, element_factory)
    pkg1 = element_factory.create(kerml.Package)
    pkg2 = element_factory.create(kerml.Package)
    part = element_factory.create(sysml2.PartDefinition)

    assert change_owner(pkg1, part)

    pkg1_item = tree_model.tree_item_for_element(pkg1)
    assert pkg1_item is not None
    pkg1_children = tree_model.child_model(pkg1_item)
    assert pkg1_children is not None
    assert any(tree_item.element is part for tree_item in pkg1_children)

    assert change_owner(pkg2, part)

    pkg2_item = tree_model.tree_item_for_element(pkg2)
    assert pkg2_item is not None
    pkg2_children = tree_model.child_model(pkg2_item)
    assert pkg2_children is not None
    assert any(tree_item.element is part for tree_item in pkg2_children)


def test_editable_text_updates_declared_name(event_manager, element_factory):
    tree_model = TreeModel(event_manager, element_factory)
    part = element_factory.create(sysml2.PartDefinition)

    tree_item = tree_model.tree_item_for_element(part)
    assert tree_item is not None

    tree_item.editable_text = "Renamed"

    assert part.declaredName == "Renamed"
