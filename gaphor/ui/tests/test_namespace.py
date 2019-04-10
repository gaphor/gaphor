import pytest
import gaphor.UML as UML
from gaphor.ui.namespace import Namespace
from gaphor.application import Application


@pytest.fixture
def application(
    services=["element_factory", "component_registry", "ui_manager", "action_manager"]
):
    Application.init(services=services)
    yield Application
    Application.shutdown()


@pytest.fixture
def element_factory(application):
    return application.get_service("element_factory")


@pytest.fixture
def component_registry(application):
    return application.get_service("component_registry")


@pytest.fixture
def namespace(application):
    namespace = Namespace()
    namespace.init()
    yield namespace
    namespace.close()


def test_new_model_is_empty(namespace):
    assert namespace.model
    assert namespace.model.get_iter_first() is None


def test_root_element(namespace, element_factory):
    element_factory.create(UML.Package)

    assert namespace.model.iter_n_children(None) == 1


def test_multiple_root_elements(namespace, element_factory):
    element_factory.create(UML.Package)
    element_factory.create(UML.Package)

    assert namespace.model.iter_n_children(None) == 2


def dump_model(model):
    def dump(i):
        while i:
            print(("  " * model.iter_depth(i)) + str(model.get_value(i, 0).name))
            dump(model.iter_children(i))
            i = model.iter_next(i)

    dump(model.get_iter_first())


def test_nested_elements(namespace, element_factory):
    p1 = element_factory.create(UML.Package)
    p1.name = "p1"
    p2 = element_factory.create(UML.Package)
    p2.name = "p2"
    p2.package = p1

    dump_model(namespace.model)

    assert p2.namespace == p1
    assert namespace.model.iter_n_children(None) == 1


def test_find_element_in_model(namespace, element_factory):
    p1 = element_factory.create(UML.Package)
    p2 = element_factory.create(UML.Package)
    p2.package = p1

    namespace.model.clear()
    p1_iter = namespace.model.append(None, [p1])
    p2_iter = namespace.model.append(p1_iter, [p2])

    assert p2.namespace == p1

    iter = namespace.iter_for_element(p1)
    assert "0" == str(namespace.model.get_path(iter))
    assert p1 is namespace.model.get_value(iter, 0)

    iter = namespace.iter_for_element(p2)
    assert "0:0" == str(namespace.model.get_path(iter))
    assert p2 is namespace.model.get_value(iter, 0)
