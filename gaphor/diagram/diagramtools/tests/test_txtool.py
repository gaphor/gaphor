from unittest.mock import Mock

from gi.repository import Gtk

from gaphor.diagram.diagramtools.txtool import TxData, on_begin, transactional_tool
from gaphor.transaction import TransactionBegin


def test_start_tx_on_begin(view, event_manager):
    event_manager.handle = Mock()
    tx_data = TxData(event_manager)
    tool = transactional_tool(Gtk.GestureDrag.new(view), event_manager)

    on_begin(tool, None, tx_data)

    assert tx_data.tx
    assert event_manager.handle.called
    assert isinstance(event_manager.handle.call_args.args[0], TransactionBegin)
