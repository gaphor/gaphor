from gi.repository import Gdk

from gaphor.diagram.inlineeditors import InlineEditor


class TextEditTool:
    """Text edit tool.

    Allows for elements that can adapt to the IEditable interface to be
    edited.
    """

    def on_key_press(self, event):
        view = self.view
        item = view.selection.hovered_item
        if (
            item
            and event.type == Gdk.EventType.KEY_PRESS
            and event.key.keyval == Gdk.KEY_F2
        ):
            return InlineEditor(item, view)
        return False

    def on_double_click(self, event):
        view = self.view
        item = view.selection.hovered_item
        if item:
            x, y = view.get_matrix_v2i(item).transform_point(event.x, event.y)
            return InlineEditor(item, view, (x, y))
        return False
