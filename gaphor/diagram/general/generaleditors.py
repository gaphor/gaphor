from gi.repository import Gtk

from gaphor.diagram.general.comment import CommentItem
from gaphor.diagram.instanteditors import InstantEditor, show_popover
from gaphor.transaction import Transaction


@InstantEditor.register(CommentItem)
def CommentItemEditor(item, view, event_manager, pos=None) -> bool:
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
    text_view.set_size_request(100, 50)
    box = view.get_item_bounding_box(item)

    frame = Gtk.Frame()
    if Gtk.get_major_version() == 3:
        frame.add(text_view)
        text_view.show()
        frame.show()
    else:
        frame.set_child(text_view)

    show_popover(frame, view, box, update_text)

    return True
