from gaphor.diagram.editors import Editor, AbstractEditor
from gaphor.diagram.general.comment import CommentItem


@Editor.register(CommentItem)
class CommentItemEditor(AbstractEditor):
    """Text edit support for Comment item."""

    def __init__(self, item):
        self._item = item

    def is_editable(self, x, y):
        return True

    def get_text(self):
        return self._item.subject.body

    def get_bounds(self):
        return None

    def update_text(self, text):
        self._item.subject.body = text

    def key_pressed(self, pos, key):
        pass
