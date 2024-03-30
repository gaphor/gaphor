# ruff: noqa: F401,F811
from gaphor import UML
from gaphor.UML import recipes
from gaphor.UML.classes.classeseditors import association_item_editor


def test_association_item_editor(diagram, element_factory, view, event_manager):
    type_a = element_factory.create(UML.Class)
    type_b = element_factory.create(UML.Class)
    item = diagram.create(
        UML.classes.AssociationItem, subject=recipes.create_association(type_a, type_b)
    )
    view.selection.hovered_item = item
    result = association_item_editor(item, view, event_manager)

    assert result is True
