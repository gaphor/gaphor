from gaphor import UML
from gaphor.core.modeling import Dependency
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.classes.dependencypropertypages import (
    DependencyItemPropertyPage,
    DependencyPropertyPage,
)


def test_dependency_property_page(diagram, element_factory, event_manager):
    subject = element_factory.create(Dependency)
    source = element_factory.create(UML.Class)
    source.name = "A"
    target = element_factory.create(UML.Class)
    target.name = "B"
    subject.client = source
    subject.supplier = target

    property_page = DependencyPropertyPage(subject, event_manager)

    widget = property_page.construct()
    head_title = find(widget, "head")
    tail_title = find(widget, "tail")
    head_text = head_title.get_text()
    tail_text = tail_title.get_text()

    assert head_text == "A"
    assert tail_text == "B"


def test_dependency_item_property_page(diagram, element_factory, event_manager):
    item = diagram.create(
        UML.classes.DependencyItem, subject=element_factory.create(Dependency)
    )
    property_page = DependencyItemPropertyPage(item, event_manager)

    widget = property_page.construct()
    dependency_combo = find(widget, "dependency-dropdown")
    dependency_combo.set_selected(2)

    assert item.dependency_type is UML.Realization


def test_dependency_item_property_page_without_subject(diagram, event_manager):
    item = diagram.create(UML.classes.DependencyItem)
    property_page = DependencyItemPropertyPage(item, event_manager)

    widget = property_page.construct()

    assert widget
