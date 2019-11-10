from typing import Optional

from gaphas.geometry import Rectangle, distance_point_point_fast
from gi.repository import Gtk

from gaphor import UML
from gaphor.core import transactional
from gaphor.diagram.classes.association import AssociationItem
from gaphor.diagram.inlineeditors import (
    InlineEditor,
    editable_text_box,
    popup_entry,
    show_popover,
)


@InlineEditor.register(AssociationItem)
def association_item_inline_editor(item, view, pos=None) -> bool:
    """Text edit support for Named items."""

    @transactional
    def update_text(text):
        print("update text", text)
        item.subject.name = text
        popover.popdown()
        return True

    @transactional
    def update_end_text(text):
        print("update text", text)
        assert end_item
        UML.parse(end_item.subject, text)
        popover.popdown()
        return True

    subject = item.subject
    if not subject:
        return False

    end_item = None
    if pos and distance_point_point_fast(item.handles()[0].pos, pos) < 50:
        end_item = item.head_end
    elif pos and distance_point_point_fast(item.handles()[-1].pos, pos) < 50:
        end_item = item.tail_end

    if end_item:
        text = UML.format(
            end_item.subject,
            visibility=True,
            is_derived=True,
            type=True,
            multiplicity=True,
            default=True,
        )
        entry = popup_entry(text, update_end_text)
        bb = end_item.name_bounds
        x, y = view.get_matrix_i2v(item).transform_point(bb.x, bb.y)
        box = Rectangle(x, y, 10, 10)
    else:
        text = item.subject.name or ""
        entry = popup_entry(text, update_text)
        box = editable_text_box(view, view.hovered_item)

    popover = show_popover(entry, view, box)
    return True
