from gaphor.core import transactional
from gaphor.diagram.inlineeditors import InlineEditor, popup_entry, show_popover
from gaphor.UML.actions.activitynodes import ForkNodeItem


@InlineEditor.register(ForkNodeItem)
def fork_node_item_inline_editor(item, view, pos=None) -> bool:
    """Text edit support for Named items."""

    @transactional
    def update_text(text):
        item.subject.joinSpec = text
        return True

    def escape():
        item.subject.joinSpec = join_spec

    subject = item.subject
    if not subject:
        return False

    join_spec = subject.joinSpec or ""
    box = view.get_item_bounding_box(view.selection.hovered_item)
    entry = popup_entry(join_spec, update_text)
    show_popover(entry, view, box, escape)
    return True
