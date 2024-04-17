from gi.repository import Gtk

from gaphor.diagram.tools.txtool import TxData, on_begin, on_end, transactional_tool
from gaphor.transaction import TransactionBegin


class MockEventManager:
    def __init__(self):
        self.events = []

    def handle(self, event):
        self.events.append(event)


def test_start_tx_on_begin(view):
    event_manager = MockEventManager()
    tx_data = TxData(event_manager)
    (tool, _key_tool) = transactional_tool(
        Gtk.GestureDrag.new(), event_manager=event_manager
    )  # type: ignore[arg-type]

    on_begin(tool, None, tx_data)
    assert tx_data.txs

    on_end(tool, None, tx_data)

    assert event_manager.events
    assert isinstance(event_manager.events[0], TransactionBegin)
    assert not tx_data.txs
