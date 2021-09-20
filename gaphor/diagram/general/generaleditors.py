from gi.repository import Gtk

from gaphor.diagram.general.comment import CommentItem
from gaphor.diagram.inlineeditors import InlineEditor, show_popover
from gaphor.transaction import Transaction


@InlineEditor.register(CommentItem)
def CommentItemInlineEditor(item, view, event_manager, pos=None) -> bool:
    def update_text():
        text = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), include_hidden_chars=True
        )
        with Transaction(event_manager):
            item.subject.body = text

    subject = item.subject
    if not subject:
        return False

    body = subject.body or ""

    buffer = Gtk.TextBuffer()
    buffer.set_text(body, -1)
    startiter, enditer = buffer.get_bounds()
    buffer.move_mark_by_name("selection_bound", startiter)
    buffer.move_mark_by_name("insert", enditer)

    text_view = Gtk.TextView.new_with_buffer(buffer)
    box = view.get_item_bounding_box(view.selection.hovered_item)

    frame = Gtk.Frame()
    frame.add(text_view)

    text_view.show()
    frame.show()

    show_popover(frame, view, box, update_text)

    return True
