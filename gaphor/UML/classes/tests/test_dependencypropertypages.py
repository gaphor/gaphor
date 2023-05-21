from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.classes.dependencypropertypages import DependencyPropertyPage


def test_dependency_property_page(diagram, element_factory):
    item = diagram.create(
        UML.classes.DependencyItem, subject=element_factory.create(UML.Dependency)
    )
    property_page = DependencyPropertyPage(item)

    widget = property_page.construct()
    dependency_combo = find(widget, "dependency-dropdown")
    dependency_combo.set_selected(2)

    assert item.dependency_type is UML.Realization


def test_dependency_property_page_without_subject(diagram, element_factory):
    item = diagram.create(UML.classes.DependencyItem)
    property_page = DependencyPropertyPage(item)

    widget = property_page.construct()

    assert widget
