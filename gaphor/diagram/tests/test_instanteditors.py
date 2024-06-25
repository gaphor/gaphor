from gaphor import UML
from gaphor.core.modeling import Dependency
from gaphor.diagram.instanteditors import named_item_editor


def test_named_item_editor_with_element(diagram, element_factory, view, event_manager):
    item = diagram.create(
        UML.classes.ClassItem, subject=element_factory.create(UML.Class)
    )
    view.selection.hovered_item = item
    result = named_item_editor(item, view, event_manager)

    assert result is True


def test_named_item_editor_with_line(diagram, element_factory, view, event_manager):
    item = diagram.create(
        UML.classes.DependencyItem, subject=element_factory.create(Dependency)
    )
    view.selection.hovered_item = item
    result = named_item_editor(item, view, event_manager)

    assert result is True


def test_named_item_editor_without_item(diagram, element_factory, view, event_manager):
    item = diagram.create(UML.classes.DependencyItem)
    result = named_item_editor(item, view, event_manager)

    assert result is False
