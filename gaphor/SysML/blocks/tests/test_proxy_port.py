from gaphas import Item

from gaphor.SysML.blocks.proxyport import ProxyPortItem


def test_proxy_port_item_conforms_to_item_protocol(diagram):
    item = ProxyPortItem(diagram)

    assert isinstance(item, Item)


def test_proxy_port_item_point(diagram):
    item = ProxyPortItem(diagram)

    assert item.point(0, 0) == 0.0
