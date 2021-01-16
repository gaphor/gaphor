from io import StringIO

import pytest
from gaphas.aspect.connector import ConnectionSink
from gaphas.aspect.connector import Connector as ConnectorAspect

from gaphor.core import Transaction
from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import Diagram, ElementFactory
from gaphor.core.modeling.elementdispatcher import ElementDispatcher
from gaphor.diagram.connectors import Connector
from gaphor.diagram.copypaste import copy, paste
from gaphor.storage import storage
from gaphor.storage.xmlwriter import XMLWriter
from gaphor.UML.modelinglanguage import UMLModelingLanguage


@pytest.fixture
def event_manager():
    return EventManager()


@pytest.fixture
def element_factory(event_manager):
    element_factory = ElementFactory(
        event_manager, ElementDispatcher(event_manager, UMLModelingLanguage())
    )
    yield element_factory
    element_factory.shutdown()


@pytest.fixture
def modeling_language():
    return UMLModelingLanguage()


@pytest.fixture
def diagram(element_factory, event_manager) -> Diagram:
    with Transaction(event_manager):
        diagram = element_factory.create(Diagram)
    yield diagram
    with Transaction(event_manager):
        diagram.unlink()


@pytest.fixture
def create(diagram, element_factory):
    def _create(item_class, element_class=None):
        return diagram.create(
            item_class,
            subject=(element_factory.create(element_class) if element_class else None),
        )

    return _create


@pytest.fixture
def saver(element_factory):
    def save():
        """Save diagram into string."""

        f = StringIO()
        storage.save(XMLWriter(f), element_factory)
        data = f.getvalue()
        f.close()

        return data

    return save


@pytest.fixture
def loader(element_factory, modeling_language):
    def load(data):
        """Load data from specified string."""
        element_factory.flush()
        assert not list(element_factory.select())

        f = StringIO(data)
        storage.load(f, factory=element_factory, modeling_language=modeling_language)
        f.close()

    return load


def allow(line, handle, item, port=None) -> bool:
    if port is None and len(item.ports()) > 0:
        port = item.ports()[0]

    adapter = Connector(item, line)
    return adapter.allow(handle, port)


def connect(line, handle, item, port=None):
    """Connect line's handle to an item.

    If port is not provided, then first port is used.
    """
    diagram = line.diagram

    connector = ConnectorAspect(line, handle, diagram.connections)
    sink = ConnectionSink(item, distance=1e4)

    connector.connect(sink)

    cinfo = diagram.connections.get_connection(handle)
    assert cinfo.connected is item
    assert cinfo.port


def disconnect(line, handle):
    """Disconnect line's handle."""
    diagram = line.diagram

    diagram.connections.disconnect_item(line, handle)
    assert not diagram.connections.get_connection(handle)


def get_connected(item, handle):
    cinfo = item.diagram.connections.get_connection(handle)
    if cinfo:
        return cinfo.connected  # type: ignore[no-any-return] # noqa: F723
    return None


def clear_model(diagram, element_factory, retain=[]):
    """Clear the model and diagram, leaving only an empty diagram."""
    for element in list(element_factory.values()):
        if element is not diagram and element not in retain:
            element.unlink()

    for item in diagram.get_all_items():
        item.unlink()


def copy_and_paste(items, diagram, element_factory, retain=[]):
    buffer = copy(items)
    return paste(buffer, diagram, element_factory.lookup)


def copy_clear_and_paste(items, diagram, element_factory, retain=[]):
    buffer = copy(items)
    clear_model(diagram, element_factory, retain)
    return paste(buffer, diagram, element_factory.lookup)
