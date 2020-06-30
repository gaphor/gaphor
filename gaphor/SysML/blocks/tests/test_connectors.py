import pytest

from gaphor.diagram.connectors import Connector
from gaphor.SysML import sysml
from gaphor.SysML.blocks.block import BlockItem
from gaphor.SysML.blocks.connectors import BlockProxyPortConnector
from gaphor.SysML.blocks.proxyport import ProxyPortItem


@pytest.fixture
def block_item(diagram, element_factory):
    return diagram.create(BlockItem, subject=element_factory.create(sysml.Block))


@pytest.fixture
def proxy_port_item(diagram):
    return diagram.create(ProxyPortItem)


def test_connection_is_allowed(diagram, block_item, proxy_port_item):
    connector = Connector(block_item, proxy_port_item)

    assert isinstance(connector, BlockProxyPortConnector)
    assert connector.allow(proxy_port_item.handles()[0], block_item.ports()[0])


def test_connect_proxy_port_to_block(diagram, block_item, proxy_port_item):
    connector = Connector(block_item, proxy_port_item)

    connected = connector.connect(proxy_port_item.handles()[0], block_item.ports()[0])

    assert connected
    assert proxy_port_item.subject
    assert proxy_port_item.subject.encapsulatedClassifier is block_item.subject
    assert proxy_port_item.subject in block_item.subject.ownedPort


def test_disconnect_proxy_port_to_block(diagram, block_item, proxy_port_item):
    connector = Connector(block_item, proxy_port_item)
    connector.connect(proxy_port_item.handles()[0], block_item.ports()[0])

    connector.disconnect(proxy_port_item.handles()[0])

    assert proxy_port_item.subject is None
    assert proxy_port_item.canvas
