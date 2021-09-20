from gaphor.core import transactional
from gaphor.diagram.inlineeditors import InlineEditor, popup_entry, show_popover
from gaphor.transaction import Transaction
from gaphor.UML.actions.activitynodes import ForkNodeItem


@InlineEditor.register(ForkNodeItem)
def fork_node_item_inline_editor(item, view, event_manager, pos=None) -> bool:
    """Text edit support for Named items."""
    commit = True

    def update_text(text):
        if not commit:
            return
        with Transaction(event_manager):
            item.subject.joinSpec = text

    @transactional
    def escape():
        nonlocal commit
        commit = False

    subject = item.subject
    if not subject:
        return False

    join_spec = subject.joinSpec or ""
    box = view.get_item_bounding_box(view.selection.hovered_item)
    entry = popup_entry(join_spec, update_text)
    show_popover(entry, view, box, escape)
    return True
