# ruff: noqa: F401,F811
import pytest

from gaphor.UML import Comment
from gaphor.UML.general import CommentItem
from gaphor.UML.general.commenteditor import comment_item_editor


@pytest.mark.asyncio
async def test_comment_item_editor(diagram, element_factory, view, event_manager):
    item = diagram.create(CommentItem, subject=element_factory.create(Comment))
    view.selection.hovered_item = item
    await view.update()
    result = comment_item_editor(item, view, event_manager)

    assert result is True
