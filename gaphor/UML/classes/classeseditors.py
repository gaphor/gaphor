from gaphas.geometry import Rectangle, distance_point_point_fast

from gaphor.core import transactional
from gaphor.core.format import format, parse
from gaphor.diagram.inlineeditors import InlineEditor, popup_entry, show_popover
from gaphor.UML.classes.association import AssociationItem


@InlineEditor.register(AssociationItem)
def association_item_inline_editor(item, view, pos=None) -> bool:
    """Text edit support for Named items."""

    @transactional
    def update_text(text):
        item.subject.name = text
        return True

    @transactional
    def update_end_text(text):
        assert end_item
        parse(end_item.subject, text)
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
        text = (
            format(
                end_item.subject,
                visibility=True,
                is_derived=True,
                type=False,
                multiplicity=True,
                default=True,
            )
            or ""
        )

        def escape():
            assert end_item
            parse(end_item.subject, text)

        entry = popup_entry(text, update_end_text)
        bb = end_item.name_bounds
        x, y = view.get_matrix_i2v(item).transform_point(bb.x, bb.y)
        box = Rectangle(x, y, 10, 10)
    else:
        text = item.subject.name or ""

        def escape():
            item.subject.name = text

        entry = popup_entry(text, update_text)

        box = item.middle_shape_size
        i2v = view.get_matrix_i2v(item)
        x, y = i2v.transform_point(box.x, box.y)
        w, h = i2v.transform_distance(box.width, box.height)
        box = Rectangle(x, y, w, h)

    show_popover(entry, view, box, escape)
    return True
