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


def test_should_not_add_non_namespace_element(namespace, element_factory):
    element_factory.create(UML.Activity)

    assert namespace.model.iter_n_children(None) == 0


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
    p2 = element_factory.create(UML.Package)
    p2.package = p1

    assert p2.namespace == p1

    iter = namespace.iter_for_element(p1)
    assert "0" == str(namespace.model.get_path(iter))
    assert p1 is namespace.model.get_value(iter, 0)

    iter = namespace.iter_for_element(p2)
    assert "0:0" == str(namespace.model.get_path(iter))
    assert p2 is namespace.model.get_value(iter, 0)


def test_delete_element(namespace, element_factory):
    p1 = element_factory.create(UML.Package)

    p1.unlink()

    assert namespace.model.iter_n_children(None) == 0


def test_only_created_element_should_be_updated(namespace, element_factory):
    """Elements should only be visible in the model if they're added through a IElementCreateEvent event."""
    p1 = element_factory.create(UML.Package)
    p2 = UML.Package(factory=element_factory)

    p2.package = p1

    assert p2.namespace == p1

    iter = namespace.iter_for_element(p1)
    assert namespace.model.iter_n_children(None) == 1
    assert namespace.model.iter_n_children(iter) == 0


def test_element_should_not_be_added_if_parent_is_not_valid(namespace, element_factory):
    p1 = element_factory.create(UML.Package)
    p2 = element_factory.create(UML.Package)

    p1.unlink()

    p2.package = p1

    assert p2.namespace == p1

    iter = namespace.iter_for_element(p1)
    assert namespace.model.iter_n_children(None) == 0
    assert namespace.model.iter_n_children(iter) == 0


def test_change_element_name(namespace, element_factory):
    # A row-changed event should be emitted to notify the view of the name change.
    p1 = element_factory.create(UML.Package)
    events = []

    def handle_row_changed(*args):
        events.append(args)

    namespace.model.connect("row-changed", handle_row_changed)

    p1.name = "pack"

    assert len(events) == 1


def test_element_factory_flush(namespace, element_factory):
    p1 = element_factory.create(UML.Package)
    assert namespace.model.get_iter_first() is not None

    element_factory.flush()

    assert namespace.model.get_iter_first() is None
