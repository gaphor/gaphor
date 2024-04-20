from __future__ import annotations

import logging
from typing import Iterable

from gi.repository import Gtk

from gaphor.core.eventmanager import EventManager
from gaphor.transaction import Transaction

log = logging.getLogger(__name__)


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
    *tools: Gtk.Gesture, event_manager: EventManager | None = None
) -> Iterable[Gtk.EventController]:
    tx_data = TxData(event_manager)
    for tool in tools:
        tool.connect("begin", on_begin, tx_data)
        tool.connect_after("end", on_end, tx_data)
        tool.connect_after("cancel", on_cancel, tx_data)

    key_ctrl = Gtk.EventControllerKey.new()
    key_ctrl.connect("key-pressed", key_pressed, tools, tx_data)
    return (*tools, key_ctrl)


def on_begin(gesture, _sequence, tx_data):
    while tx_data.txs:
        log.warning(
            "Closing transaction. This should have happened in the 'end' handler."
        )
        tx_data.commit()

    tx_data.begin()


def on_cancel(gesture, _sequence, tx_data):
    if tx_data.txs:
        Transaction.mark_rollback()


def on_end(gesture, _sequence, tx_data):
    tx_data.commit()


def key_pressed(ctrl, keyval, keycode, state, tools, tx_data):
    if tx_data.txs:
        for tool in tools:
            tool.reset()
        return True
