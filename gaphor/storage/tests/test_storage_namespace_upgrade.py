import pytest

from gaphor import UML
from gaphor.C4Model import c4model
from gaphor.core.modeling import ElementFactory
from gaphor.core.modeling.elementdispatcher import ElementDispatcher
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.storage.parser import element
from gaphor.storage.tests.test_storage_uml_2_5_upgrade import loader  # noqa: F401


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


@pytest.mark.parametrize(
    "old_name,new_type",
    [
        ["C4Container", c4model.Container],
        ["C4Person", c4model.Person],
        ["C4Database", c4model.Database],
        ["C4Dependency", c4model.Dependency],
    ],
)
def test_c4_elements(old_name, new_type, loader):  # noqa: F811
    parsed_item = element(id="2", type=old_name)
    elem = loader(parsed_item)[0]

    assert elem.__class__ is new_type


def test_uml_dependency(loader):  # noqa: F811
    parsed_item = element(id="2", type="Dependency")
    elem = loader(parsed_item)[0]

    assert elem.__class__ is UML.Dependency
