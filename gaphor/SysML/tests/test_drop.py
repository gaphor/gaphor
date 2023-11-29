from gaphor import UML
from gaphor.diagram.drop import drop
from gaphor.SysML import sysml
from gaphor.SysML.blocks import PropertyItem, ProxyPortItem
from gaphor.UML.recipes import create_connector


def test_drop_sysml_diagram(diagram, element_factory):
    sysml_diagram = element_factory.create(sysml.SysMLDiagram)

    item = drop(sysml_diagram, diagram, 0, 0)

    assert item


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


def test_drop_proxy_port_on_property(diagram, element_factory):
    block = element_factory.create(sysml.Block)
    prop = element_factory.create(UML.Property)
    prop.type = block

    property_item = drop(prop, diagram, 0, 0)
    assert property_item

    port = element_factory.create(sysml.ProxyPort)
    assert not drop(
        port, diagram, 0, 0
    ), "unable to add port when there is no item that it can be attached to"

    block.ownedPort.append(port)

    port_item = drop(port, diagram, 0, 0)
    assert isinstance(port_item, ProxyPortItem), "port was added"
    assert port_item in property_item.children, "port is attached to the property item"

    property_item_2 = drop(prop, diagram, 500, 500)
    assert property_item_2

    port_item = drop(port, diagram, 500, 500)
    assert isinstance(port_item, ProxyPortItem), "port was added"
    assert (
        port_item in property_item_2.children
    ), "port is attached to the second property item"

    port_item = drop(port, diagram, 100, 200)
    assert isinstance(port_item, ProxyPortItem), "port was added"
    assert (
        port_item in property_item.children
    ), "port is attached to the first property item"
