import pytest
from gaphor.application import Application
from gaphor.UML.elementfactory import ElementFactory
from gaphor.storage.storage import load_elements
from gaphor.storage.parser import element, canvas, canvasitem


@pytest.fixture
def application(services=["element_factory", "action_manager"]):
    Application.init(services=services)
    yield Application
    Application.shutdown()


@pytest.fixture
def element_factory(application):
    return application.get_service("element_factory")


def test_upgrade_metaclass_item_to_class_item(element_factory):
    elements = {
        "1": element(
            id="1",
            type="Diagram",
            canvas=canvas(canvasitems=[canvasitem(id="2", type="MetaclassItem")]),
        )
    }

    load_elements(elements, element_factory)

    assert element_factory.size() == 1
