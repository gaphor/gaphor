from gaphor.core import transactional
from gaphor.diagram.inlineeditors import InlineEditor, popup_entry, show_popover
from gaphor.UML.actions.activitynodes import ForkNodeItem


@InlineEditor.register(ForkNodeItem)
def fork_node_item_inline_editor(item, view, pos=None) -> bool:
    """Text edit support for Named items."""

    @transactional
    def update_text(text):
        item.subject.joinSpec = text
        popover.popdown()
        return True

    subject = item.subject
    if not subject:
        return False

    box = view.get_item_bounding_box(view.hovered_item)
    entry = popup_entry(subject.joinSpec or "", update_text)
    popover = show_popover(entry, view, box)
    return True
