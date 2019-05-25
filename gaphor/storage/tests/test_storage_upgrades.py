import pytest
from gaphor.application import Application
from gaphor.UML.elementfactory import ElementFactory
from gaphor.storage.storage import load_elements
from gaphor.storage.parser import element, canvas, canvasitem
from gaphor.storage import diagramitems


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

    item = element_factory.lselect()[0].canvas.get_root_items()[0]
    assert type(item) == diagramitems.ClassItem


def test_upgrade_subsystem_item_to_class_item(element_factory):
    elements = {
        "1": element(
            id="1",
            type="Diagram",
            canvas=canvas(canvasitems=[canvasitem(id="2", type="SubsystemItem")]),
        )
    }

    load_elements(elements, element_factory)
    item = element_factory.lselect()[0].canvas.get_root_items()[0]
    assert type(item) == diagramitems.ComponentItem
