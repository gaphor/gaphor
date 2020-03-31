from io import StringIO

import pytest
from gaphas.aspect import ConnectionSink
from gaphas.aspect import Connector as ConnectorAspect

from gaphor import UML
from gaphor.diagram.connectors import Connector
from gaphor.misc.xmlwriter import XMLWriter
from gaphor.services.eventmanager import EventManager
from gaphor.storage import storage
from gaphor.UML.elementfactory import ElementFactory


@pytest.fixture
def event_manager():
    return EventManager()


@pytest.fixture
def element_factory(event_manager):
    return ElementFactory(event_manager)


@pytest.fixture
def diagram(element_factory):
    return element_factory.create(UML.Diagram)


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
def loader(element_factory):
    def load(data):
        """
        Load data from specified string.
        """
        element_factory.flush()
        assert not list(element_factory.select())

        f = StringIO(data)
        storage.load(f, factory=element_factory)
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
