import pytest
from gaphor.UML.elementfactory import ElementFactory
from gaphor.services.eventmanager import EventManager
from gaphor.storage.storage import load_elements
from gaphor.storage.parser import element, canvas, canvasitem
from gaphor.storage import diagramitems


@pytest.fixture
def element_factory():
    return ElementFactory(EventManager())


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
