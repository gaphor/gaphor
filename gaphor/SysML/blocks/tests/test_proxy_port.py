import pytest
from gaphas import Item

from gaphor.core.modeling import Diagram
from gaphor.diagram.tests.fixtures import connect
from gaphor.SysML.blocks.block import BlockItem
from gaphor.SysML.blocks.proxyport import ProxyPortItem
from gaphor.SysML.sysml import Block


def test_proxy_port_item_conforms_to_item_protocol(diagram):
    item = ProxyPortItem(diagram)

    assert isinstance(item, Item)


def test_proxy_port_item_point(diagram):
    item = ProxyPortItem(diagram)

    assert item.point(0, 0) == pytest.approx(0.0)


def test_ports(diagram):
    proxy_port = diagram.create(ProxyPortItem)

    diagram.update({proxy_port})

    top, right, bottom, left = proxy_port.ports()

    def pos(p):
        return p.x, p.y

    assert pos(proxy_port.handles()[0].pos) == (0, 0)
    assert pos(left.end) == pos(top.start) == (-8, -8)
    assert pos(top.end) == pos(right.start) == (8, -8)
    assert pos(right.end) == pos(bottom.start) == (8, 8)
    assert pos(bottom.end) == pos(left.start) == (-8, 8)


def test_save_load(create, saver, loader, element_factory):
    proxy_port = create(ProxyPortItem)
    block = create(BlockItem, Block)

    connect(proxy_port, proxy_port.handles()[0], block)

    data = saver()
    loader(data)

    new_diagram = next(element_factory.select(Diagram))
    new_proxy_port = next(element_factory.select(ProxyPortItem))
    new_block = next(element_factory.select(BlockItem))
    connected = new_diagram.connections.get_connection(
        new_proxy_port.handles()[0]
    ).connected

    assert connected is new_block
