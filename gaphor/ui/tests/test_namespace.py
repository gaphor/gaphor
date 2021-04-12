import pytest

from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.ui.namespace import Namespace, popup_model


@pytest.fixture
def namespace(event_manager, element_factory):
    ns = Namespace(event_manager, element_factory)
    scrolled_window = ns.open()  # noqa: F841
    assert ns.model
    assert ns.view
    yield ns
    ns.shutdown()


def test_popup_model(namespace, diagram, element_factory):
    item = diagram.create(
        UML.classes.ClassItem, subject=element_factory.create(UML.Class)
    )
    namespace.select_element(item.subject)

    popup = popup_model(namespace.view)

    assert popup


def test_create_diagram(namespace, element_factory):
    package = element_factory.create(UML.Package)
    namespace.select_element(package)

    namespace.tree_view_create_diagram()

    assert element_factory.lselect(Diagram)


def test_create_package(namespace, element_factory):
    package = element_factory.create(UML.Package)
    namespace.select_element(package)

    namespace.tree_view_create_package()

    assert element_factory.lselect(lambda e: e.namespace is package)


def test_delete_package(namespace, element_factory):
    package = element_factory.create(UML.Package)
    namespace.select_element(package)

    namespace.tree_view_delete()

    assert element_factory.lselect() == []
