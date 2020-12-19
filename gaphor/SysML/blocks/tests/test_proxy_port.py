import pytest
from gaphas import Item
from gaphas.connections import Connections

from gaphor.SysML.blocks.proxyport import ProxyPortItem


@pytest.fixture
def connections():
    return Connections()


def test_proxy_port_item_conforms_to_item_protocol(connections):
    item = ProxyPortItem(connections)

    assert isinstance(item, Item)
