from __future__ import annotations

from gi.repository import Gtk

from gaphor.core.eventmanager import EventManager
from gaphor.transaction import Transaction


class TxData:
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.txs: list[Transaction] = []

    def begin(self):
        self.txs.append(Transaction(self.event_manager))

    def commit(self):
        assert self.txs
        tx = self.txs.pop()
        tx.commit()


def transactional_tool(
    *tools: Gtk.EventController, event_manager: EventManager | None = None
):
    tx_data = TxData(event_manager)
    for tool in tools:
        if not isinstance(tool, Gtk.EventControllerKey):
            tool.connect("begin", on_begin, tx_data)
            tool.connect_after("end", on_end, tx_data)
        else:
            tool.connect_after("key-pressed", key_pressed, tx_data)
    return tools


def on_begin(gesture, _sequence, tx_data):
    tx_data.begin()


def on_end(gesture, _sequence, tx_data):
    tx_data.commit()


def key_pressed(ctrl, keyval, keycode, _sequence, tx_data):
    if len(tx_data.txs) > 0:
        tx_data.commit()
        view = ctrl.get_widget()
        view.selection.grayed_out_items = set()
        view.selection.dropzone_item = None
