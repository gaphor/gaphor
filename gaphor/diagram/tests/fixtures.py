import pytest
from gaphas.aspect import ConnectionSink, Connector

from gaphor import UML
from gaphor.diagram.connectors import IConnect
from gaphor.services.eventmanager import EventManager
from gaphor.UML.elementfactory import ElementFactory


@pytest.fixture
def element_factory():
    return ElementFactory(EventManager())


@pytest.fixture
def diagram(element_factory):
    return element_factory.create(UML.Diagram)


def allow(line, handle, item, port=None):
    if port is None and len(item.ports()) > 0:
        port = item.ports()[0]

    adapter = IConnect(item, line)
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
    connector = Connector(line, handle)

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
