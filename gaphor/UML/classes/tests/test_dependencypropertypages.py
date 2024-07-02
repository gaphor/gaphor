from gaphor import UML
from gaphor.core.modeling import Dependency
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.classes.dependencypropertypages import DependencyPropertyPage


def test_dependency_property_page(diagram, element_factory, event_manager):
    item = diagram.create(
        UML.classes.DependencyItem, subject=element_factory.create(Dependency)
    )
    property_page = DependencyPropertyPage(item, event_manager)

    widget = property_page.construct()
    dependency_combo = find(widget, "dependency-dropdown")
    dependency_combo.set_selected(2)

    assert item.dependency_type is UML.Realization


def test_dependency_property_page_without_subject(diagram, event_manager):
    item = diagram.create(UML.classes.DependencyItem)
    property_page = DependencyPropertyPage(item, event_manager)

    widget = property_page.construct()

    assert widget
