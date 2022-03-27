from gaphor import UML
from gaphor.diagram.drop import drop
from gaphor.SysML import sysml
from gaphor.SysML.blocks import PropertyItem, ProxyPortItem
from gaphor.UML.recipes import create_connector


def test_drop_connector(diagram, element_factory):
    proxy_port = element_factory.create(sysml.ProxyPort)
    proxy_port_item = diagram.create(ProxyPortItem, subject=proxy_port)
    property = element_factory.create(UML.Property)
    property_item = diagram.create(PropertyItem, subject=property)
    connector = create_connector(proxy_port, property)

    item = drop(connector, diagram, 0, 0)

    assert item
    assert diagram.connections.get_connection(item.head).connected is proxy_port_item
    assert diagram.connections.get_connection(item.tail).connected is property_item


def test_drop_proxy_port(diagram, element_factory):
    block = element_factory.create(sysml.Block)
    proxy_port = element_factory.create(sysml.ProxyPort)
    proxy_port.encapsulatedClassifier = block

    drop(block, diagram, 0, 0)

    item = drop(proxy_port, diagram, 0, 0)

    assert item
    assert (
        diagram.connections.get_connection(item.handles()[0]).connected
        is block.presentation[0]
    )
