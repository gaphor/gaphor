from gi.repository import Gdk, Gtk

from gaphor.core import transactional
from gaphor.diagram.general.comment import CommentItem
from gaphor.diagram.inlineeditors import InlineEditor, show_popover


@InlineEditor.register(CommentItem)
def CommentItemInlineEditor(item, view, pos=None) -> bool:
    @transactional
    def update_text():
        text = buffer.get_text(
            buffer.get_start_iter(), buffer.get_end_iter(), include_hidden_chars=True
        )
        item.subject.body = text
        return True

    def on_key_press_event(widget, event):
        if event.keyval == Gdk.KEY_Return and not event.get_state() & (
            Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK
        ):
            popover.popdown()
            return True

    def escape():
        subject.body = body

    subject = item.subject
    if not subject:
        return False

    body = subject.body or ""

    buffer = Gtk.TextBuffer()
    buffer.set_text(body, -1)
    startiter, enditer = buffer.get_bounds()
    buffer.move_mark_by_name("selection_bound", startiter)
    buffer.move_mark_by_name("insert", enditer)
    buffer.connect("changed", lambda _: update_text())

    text_view = Gtk.TextView.new_with_buffer(buffer)
    text_view.connect("key-press-event", on_key_press_event)
    box = view.get_item_bounding_box(view.hovered_item)

    frame = Gtk.Frame()
    frame.add(text_view)

    text_view.show()
    frame.show()

    popover = show_popover(frame, view, box, escape)
    return True
