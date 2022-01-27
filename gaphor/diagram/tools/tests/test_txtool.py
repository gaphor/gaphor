import pytest
from gi.repository import Gtk

from gaphor.diagram.tools.txtool import TxData, on_begin, on_end, transactional_tool
from gaphor.transaction import TransactionBegin


@pytest.fixture(autouse=True)
def window(view):
    if Gtk.get_major_version() == 3:
        window = Gtk.Window.new(Gtk.WindowType.TOPLEVEL)
        window.add(view)
        window.show_all()
    else:
        window = Gtk.Window.new()
        window.set_child(view)
        window.show()
    yield window
    window.destroy()


class MockEventManager:
    def __init__(self):
        self.events = []

    def handle(self, event):
        self.events.append(event)


def test_start_tx_on_begin(view):
    event_manager = MockEventManager()
    tx_data = TxData(event_manager)
    if Gtk.get_major_version() == 3:
        (tool,) = transactional_tool(Gtk.GestureDrag.new(view), event_manager=event_manager)  # type: ignore[arg-type]
    else:
        (tool,) = transactional_tool(Gtk.GestureDrag.new(), event_manager=event_manager)  # type: ignore[arg-type]

    on_begin(tool, None, tx_data)
    assert tx_data.txs

    on_end(tool, None, tx_data)

    assert event_manager.events
    assert isinstance(event_manager.events[0], TransactionBegin)
