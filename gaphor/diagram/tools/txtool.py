from typing import Iterable, List

from gi.repository import Gtk

from gaphor.core.eventmanager import EventManager
from gaphor.transaction import Transaction


class TxData:
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.txs: List[Transaction] = []

    def begin(self):
        self.txs.append(Transaction(self.event_manager))

    def commit(self):
        if not self.txs:
            return
        tx = self.txs.pop()
        tx.commit()


def transactional_tool(
    *tools: Gtk.Gesture, event_manager: EventManager = None
) -> Iterable[Gtk.Gesture]:
    tx_data = TxData(event_manager)
    for tool in tools:
        tool.connect("sequence-state-changed", on_sequence_claimed, tx_data)
        tool.connect_after("end", on_end, tx_data)
    return tools


def on_sequence_claimed(gesture, _sequence, state, tx_data):
    if state == Gtk.EventSequenceState.CLAIMED:
        tx_data.begin()


def on_end(gesture, _sequence, tx_data):
    tx_data.commit()
