from gaphor.diagram.editors import Editor, AbstractEditor, NamedItemEditor
from gaphor.diagram.actions.action import ActionItem
from gaphor.diagram.actions.activitynodes import ForkNodeItem


Editor.register(ActionItem, NamedItemEditor)


@Editor.register(ForkNodeItem)
class ForkNodeItemEditor(AbstractEditor):
    """Text edit support for fork node join specification."""

    def __init__(self, item):
        self._item = item

    def is_editable(self, x, y):
        return True

    def get_text(self):
        """
        Get join specification text.
        """
        if self._item.subject.joinSpec:
            return self._item.subject.joinSpec
        else:
            return ""

    def get_bounds(self):
        return None

    def update_text(self, text):
        """
        Set join specification text.
        """
        spec = self._item.subject.joinSpec
        if not spec:
            spec = text

    def key_pressed(self, pos, key):
        pass
