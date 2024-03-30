# ruff: noqa: F401,F811
from gaphor.core.modeling import Comment
from gaphor.diagram.general import CommentItem
from gaphor.diagram.general.generaleditors import comment_item_editor


def test_comment_item_editor(diagram, element_factory, view, event_manager):
    item = diagram.create(CommentItem, subject=element_factory.create(Comment))
    view.selection.hovered_item = item
    result = comment_item_editor(item, view, event_manager)

    assert result is True
