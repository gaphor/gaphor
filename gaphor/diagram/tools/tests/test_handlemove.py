from gaphas.handlemove import HandleMove

from gaphor.core import event_handler
from gaphor.core.modeling import Comment
from gaphor.diagram.connectors import ItemTemporaryDisconnected
from gaphor.diagram.general import CommentItem, CommentLineItem
from gaphor.diagram.presentation import LinePresentation
from gaphor.diagram.tests.fixtures import connect


def test_handle_move_has_guides(create, view):
    line = create(LinePresentation)

    handle_move = HandleMove(line, line.handles()[0], view)

    handle_move.start_move((0, 0))
    handle_move.move((0, 0))

    assert view.guides


def test_handle_move_has_gray_out(create, view):
    line = create(CommentLineItem)
    line2 = create(CommentLineItem)

    handle_move = HandleMove(line, line.handles()[0], view)

    handle_move.start_move((0, 0))

    assert line2 in view.selection.grayed_out_items


def test_handle_move_sends_disconnect_event(create, view, event_manager):
    comment = create(CommentItem, element_class=Comment)
    line = create(CommentLineItem)
    connect(line, line.handles()[0], comment)

    events = []

    @event_handler(ItemTemporaryDisconnected)
    def handler(e):
        events.append(e)

    event_manager.subscribe(handler)

    handle_move = HandleMove(line, line.handles()[0], view)
    handle_move.start_move((0, 0))

    assert events
