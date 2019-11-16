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
        popover.popdown()
        return True

    subject = item.subject
    if not subject:
        return False

    def on_key_press_event(widget, event):
        if event.keyval == Gdk.KEY_Return and not event.get_state() & (
            Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK
        ):
            update_text()
        elif event.keyval == Gdk.KEY_Escape:
            widget.get_toplevel().destroy()

    def on_focus_out_event(widget, event):
        update_text()

    buffer = Gtk.TextBuffer()
    buffer.set_text((subject.body or "") if subject else "", -1)
    startiter, enditer = buffer.get_bounds()
    buffer.move_mark_by_name("selection_bound", startiter)
    buffer.move_mark_by_name("insert", enditer)

    text_view = Gtk.TextView.new_with_buffer(buffer)
    text_view.connect("focus-out-event", on_focus_out_event)
    text_view.connect("key-press-event", on_key_press_event)
    box = view.get_item_bounding_box(view.hovered_item)

    frame = Gtk.Frame()
    frame.set_shadow_type(Gtk.ShadowType.IN)
    frame.add(text_view)

    text_view.show()
    frame.show()
    popover = show_popover(frame, view, box)
    return True
