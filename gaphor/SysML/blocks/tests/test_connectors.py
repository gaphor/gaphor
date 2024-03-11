import pytest

from gaphor import UML
from gaphor.diagram.connectors import Connector
from gaphor.diagram.tests.fixtures import allow, connect, disconnect
from gaphor.SysML import sysml
from gaphor.SysML.blocks.block import BlockItem
from gaphor.SysML.blocks.connectors import BlockProperyProxyPortConnector
from gaphor.SysML.blocks.property import PropertyItem
from gaphor.SysML.blocks.proxyport import ProxyPortItem
from gaphor.UML.deployments import ConnectorItem


@pytest.fixture
def block_item(diagram, element_factory):
    return diagram.create(BlockItem, subject=element_factory.create(sysml.Block))


@pytest.fixture
def property_item(diagram, element_factory):
    type = element_factory.create(sysml.Block)
    prop = diagram.create(PropertyItem, subject=element_factory.create(sysml.Property))
    prop.subject.type = type
    return prop


@pytest.fixture
def proxy_port_item(diagram):
    return diagram.create(ProxyPortItem)


def connected_proxy_port_item(diagram, element_factory):
    proxy_port_item = diagram.create(ProxyPortItem)
    block_item = diagram.create(BlockItem, subject=element_factory.create(sysml.Block))

    connector = Connector(block_item, proxy_port_item)
    connector.connect(proxy_port_item.handles()[0], block_item.ports()[0])

    return proxy_port_item


@pytest.fixture
def head_proxy_port_item(diagram, element_factory):
    return connected_proxy_port_item(diagram, element_factory)


@pytest.fixture
def tail_proxy_port_item(diagram, element_factory):
    return connected_proxy_port_item(diagram, element_factory)


@pytest.fixture
def other_proxy_port_item(diagram, element_factory):
    return connected_proxy_port_item(diagram, element_factory)


@pytest.fixture
def connector_item(diagram):
    return diagram.create(ConnectorItem)


def test_connection_is_allowed(block_item, proxy_port_item):
    connector = Connector(block_item, proxy_port_item)

    assert isinstance(connector, BlockProperyProxyPortConnector)
    assert connector.allow(proxy_port_item.handles()[0], block_item.ports()[0])


def test_connect_proxy_port_to_block(block_item, proxy_port_item):
    connector = Connector(block_item, proxy_port_item)

    connected = connector.connect(proxy_port_item.handles()[0], block_item.ports()[0])

    assert connected
    assert proxy_port_item.subject
    assert proxy_port_item.subject.encapsulatedClassifier is block_item.subject
    assert proxy_port_item.subject in block_item.subject.ownedPort


def test_disconnect_proxy_port_to_block(block_item, proxy_port_item):
    connector = Connector(block_item, proxy_port_item)
    connector.connect(proxy_port_item.handles()[0], block_item.ports()[0])

    connector.disconnect(proxy_port_item.handles()[0])

    assert proxy_port_item.subject is None
    assert proxy_port_item.diagram


def test_connect_proxy_port_to_property(property_item, proxy_port_item):
    connector = Connector(property_item, proxy_port_item)

    connected = connector.connect(
        proxy_port_item.handles()[0], property_item.ports()[0]
    )

    assert connected
    assert proxy_port_item.subject
    assert proxy_port_item.subject.encapsulatedClassifier is property_item.subject.type
    assert proxy_port_item.subject in property_item.subject.type.ownedPort


def test_allow_connector_to_proxy_port(
    connector_item: ConnectorItem, head_proxy_port_item: ProxyPortItem
):
    assert allow(connector_item, connector_item.handles()[0], head_proxy_port_item)


def test_connect_connector_on_one_end_to_proxy_port(
    connector_item: ConnectorItem, head_proxy_port_item: ProxyPortItem
):
    connect(connector_item, connector_item.handles()[0], head_proxy_port_item)

    assert connector_item.subject is None


def test_connect_connector_on_both_ends_to_proxy_port(
    connector_item: ConnectorItem,
    head_proxy_port_item: ProxyPortItem,
    tail_proxy_port_item: ProxyPortItem,
):
    connect(connector_item, connector_item.handles()[0], head_proxy_port_item)
    connect(connector_item, connector_item.handles()[1], tail_proxy_port_item)

    assert connector_item.subject
    assert head_proxy_port_item.subject in connector_item.subject.end[:].role
    assert tail_proxy_port_item.subject in connector_item.subject.end[:].role


def test_disconnect_connector_from_proxy_port(
    connector_item: ConnectorItem,
    head_proxy_port_item: ProxyPortItem,
    tail_proxy_port_item: ProxyPortItem,
    element_factory,
    sanitizer_service,
):
    connect(connector_item, connector_item.handles()[0], head_proxy_port_item)
    connect(connector_item, connector_item.handles()[1], tail_proxy_port_item)

    disconnect(connector_item, connector_item.handles()[0])

    assert not connector_item.subject
    assert element_factory.lselect(UML.Connector) == []
    assert element_factory.lselect(UML.ConnectorEnd) == []
    assert head_proxy_port_item.subject in element_factory.select(UML.Port)
    assert tail_proxy_port_item.subject in element_factory.select(UML.Port)
