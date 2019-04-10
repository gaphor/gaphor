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


def test_root_element_in_model(namespace, element_factory):
    element_factory.create(UML.Package)

    assert namespace.model.iter_n_children(None) == 1
