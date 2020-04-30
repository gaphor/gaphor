from io import StringIO

import pytest
from gaphas.aspect import ConnectionSink
from gaphas.aspect import Connector as ConnectorAspect

from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import Diagram, ElementFactory
from gaphor.core.modeling.elementdispatcher import ElementDispatcher
from gaphor.diagram.connectors import Connector
from gaphor.storage import storage
from gaphor.storage.xmlwriter import XMLWriter
from gaphor.UML.modelinglanguage import UMLModelingLanguage


@pytest.fixture
def event_manager():
    return EventManager()


@pytest.fixture
def element_factory(event_manager):
    return ElementFactory(
        event_manager, ElementDispatcher(event_manager, UMLModelingLanguage())
    )


@pytest.fixture
def modeling_language():
    return UMLModelingLanguage()


@pytest.fixture
def diagram(element_factory):
    diagram = element_factory.create(Diagram)
    yield diagram
    diagram.unlink()


@pytest.fixture
def saver(element_factory):
    def save():
        """
        Save diagram into string.
        """

        f = StringIO()
        storage.save(XMLWriter(f), element_factory)
        data = f.getvalue()
        f.close()

        return data

    return save


@pytest.fixture
def loader(element_factory, modeling_language):
    def load(data):
        """
        Load data from specified string.
        """
        element_factory.flush()
        assert not list(element_factory.select())

        f = StringIO(data)
        storage.load(f, factory=element_factory, modeling_language=modeling_language)
        f.close()

    return load


def allow(line, handle, item, port=None):
    if port is None and len(item.ports()) > 0:
        port = item.ports()[0]

    adapter = Connector(item, line)
    return adapter.allow(handle, port)


def connect(line, handle, item, port=None):
    """
    Connect line's handle to an item.

    If port is not provided, then first port is used.
    """
    canvas = line.canvas

    if port is None and len(item.ports()) > 0:
        port = item.ports()[0]

    sink = ConnectionSink(item, port)
    connector = ConnectorAspect(line, handle)

    connector.connect(sink)

    cinfo = canvas.get_connection(handle)
    assert cinfo.connected is item
    assert cinfo.port is port


def disconnect(line, handle):
    """
    Disconnect line's handle.
    """
    canvas = line.canvas

    canvas.disconnect_item(line, handle)
    assert not canvas.get_connection(handle)


def clear_model(diagram, element_factory):
    """
    Clear the model and diagram, leaving only an empty diagram.
    """
    for element in list(element_factory.values()):
        if element is not diagram:
            element.unlink()

    for item in diagram.canvas.get_all_items():
        item.unlink()
