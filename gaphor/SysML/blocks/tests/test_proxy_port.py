from gaphas import Item

from gaphor.SysML.blocks.proxyport import ProxyPortItem


def test_proxy_port_item_conforms_to_item_protocol(diagram):
    item = ProxyPortItem(diagram)

    assert isinstance(item, Item)
