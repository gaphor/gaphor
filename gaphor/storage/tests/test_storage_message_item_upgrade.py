import pytest
import importlib_metadata

from gaphor import UML
from gaphor.application import Application
from gaphor.storage.storage import load_elements
from gaphor.storage.parser import parse
from gaphor.storage import diagramitems


@pytest.fixture
def application():
    Application.init(
        services=["event_manager", "component_registry", "element_factory"]
    )
    yield Application
    Application.shutdown()


@pytest.fixture
def element_factory(application):
    return application.get_service("element_factory")


def test_message_item_upgrade(element_factory):
    """
    """
    dist = importlib_metadata.distribution("gaphor")
    path = dist.locate_file("test-diagrams/multiple-messages.gaphor")

    elements = parse(path)
    load_elements(elements, element_factory)

    diagram = element_factory.lselect(lambda e: e.isKindOf(UML.Diagram))[0]
    items = diagram.canvas.get_root_items()
    message_items = [i for i in items if isinstance(i, diagramitems.MessageItem)]
    subjects = [m.subject for m in message_items]
    messages = element_factory.lselect(lambda e: e.isKindOf(UML.Message))
    presentations = [m.presentation for m in messages]

    assert len(messages) == 10
    assert all(subjects), subjects
    assert len(message_items) == 10
    assert all(presentations), presentations
