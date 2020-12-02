from gi.repository import Gtk

from gaphor.transaction import Transaction


class TxData:
    def __init__(self, event_manager):
        self.event_manager = event_manager
        self.tx = None


def transactional_tool(tool: Gtk.Gesture, event_manager):
    tx_data = TxData(event_manager)
    tool.connect("begin", on_begin, tx_data)
    tool.connect("end", on_end, tx_data)
    tool.connect("cancel", on_cancel, tx_data)
    return tool


def on_begin(gesture, _sequence, tx_data):
    tx_data.tx = Transaction(tx_data.event_manager)


def on_end(gesture, _sequence, tx_data):
    if tx_data.tx:
        tx_data.tx.commit()
        tx_data.tx = None


def on_cancel(gesture, _sequence, tx_data):
    if tx_data.tx:
        tx_data.tx.rollback()
        tx_data.tx = None
