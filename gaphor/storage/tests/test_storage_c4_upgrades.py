import pytest

from gaphor.core.modeling import ElementFactory
from gaphor.core.modeling.elementdispatcher import ElementDispatcher
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.storage.parser import element
from gaphor.storage.tests.test_storage_upgrades import loader  # noqa: F401


@pytest.fixture
def modeling_language(event_manager):
    return ModelingLanguageService(event_manager)


@pytest.fixture
def element_factory(event_manager, modeling_language):
    element_factory = ElementFactory(
        event_manager, ElementDispatcher(event_manager, modeling_language)
    )
    yield element_factory
    element_factory.shutdown()


def test_c4_database_item(loader):  # noqa: F811
    parsed_item = element(id="2", type="C4ContainerDatabaseItem")
    item = loader(parsed_item)[0]

    assert item.__class__.__name__ == "C4DatabaseItem"
