from gaphor import UML
from gaphor.diagram.instanteditors import instant_editor, popup_entry, show_popover
from gaphor.transaction import Transaction
from gaphor.UML.actions.activity import ActivityParameterNodeItem
from gaphor.UML.actions.activitynodes import ForkNodeItem


@instant_editor.register(ForkNodeItem)
def fork_node_item_editor(item, view, event_manager, pos=None) -> bool:
    """Text edit support for Named items."""

    subject = item.subject
    if not isinstance(subject, UML.JoinNode):
        return False

    join_spec = subject.joinSpec or ""
    box = view.get_item_bounding_box(view.selection.hovered_item)
    entry = popup_entry(join_spec)

    def update_text():
        with Transaction(event_manager):
            item.subject.joinSpec = entry.get_buffer().get_text()

    show_popover(entry, view, box, update_text)
    return True


@instant_editor.register(ActivityParameterNodeItem)
def activity_parameter_node_item_editor(
    item: ActivityParameterNodeItem, view, event_manager, pos=None
) -> bool:
    subject = item.subject
    if not subject or not subject.parameter:
        return False

    name = subject.parameter.name or ""
    box = view.get_item_bounding_box(view.selection.hovered_item)
    entry = popup_entry(name)

    def update_text():
        with Transaction(event_manager):
            item.subject.parameter.name = entry.get_buffer().get_text()

    show_popover(entry, view, box, update_text)
    return True
