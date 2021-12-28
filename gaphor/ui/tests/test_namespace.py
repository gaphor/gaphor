import pytest

from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.ui.namespace import Namespace, popup_model
from gaphor.UML.modelinglanguage import UMLModelingLanguage


@pytest.fixture
def namespace(event_manager, element_factory, modeling_language):
    ns = Namespace(event_manager, element_factory, modeling_language)
    scrolled_window = ns.open()  # noqa: F841
    assert ns.model
    assert ns.view
    yield ns
    ns.shutdown()


@pytest.fixture
def modeling_language():
    return UMLModelingLanguage()


def test_popup_model(namespace, diagram, element_factory, modeling_language):
    item = diagram.create(
        UML.classes.ClassItem, subject=element_factory.create(UML.Class)
    )
    namespace.select_element(item.subject)

    popup = popup_model(namespace.get_selected_element(), modeling_language)

    assert popup


def test_create_diagram(namespace, element_factory):
    package = element_factory.create(UML.Package)
    namespace.select_element(package)

    namespace.tree_view_create_diagram("")

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
