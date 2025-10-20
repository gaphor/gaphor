import pytest
from gi.repository import Gdk

from gaphor.diagram.tools.itemmovetool import item_move_tool, on_key_pressed
from gaphor.UML import Comment
from gaphor.UML.general import CommentItem


@pytest.mark.parametrize(
    "key,dx,dy",
    [
        (Gdk.KEY_Up, 0, -12),
        (Gdk.KEY_Down, 0, 12),
        (Gdk.KEY_Left, -12, 0),
        (Gdk.KEY_Right, 12, 0),
        (Gdk.KEY_KP_Up, 0, -12),
        (Gdk.KEY_KP_Down, 0, 12),
        (Gdk.KEY_KP_Left, -12, 0),
        (Gdk.KEY_KP_Right, 12, 0),
    ],
)
def test_item_move_by_keyboard(create, view, event_manager, key, dx, dy):
    comment = create(CommentItem, element_class=Comment)

    tool = item_move_tool(event_manager)
    view.add_controller(tool)
    view.selection.select_items(comment)

    handled = on_key_pressed(tool, key, None, None, event_manager)

    assert handled
    assert tuple(comment.matrix) == (1.0, 0.0, 0.0, 1.0, dx, dy)


def test_should_not_handle_other_keys(create, view, event_manager):
    comment = create(CommentItem, element_class=Comment)

    tool = item_move_tool(event_manager)
    view.add_controller(tool)
    view.selection.select_items(comment)

    handled = on_key_pressed(tool, Gdk.KEY_a, None, None, event_manager)

    assert not handled
