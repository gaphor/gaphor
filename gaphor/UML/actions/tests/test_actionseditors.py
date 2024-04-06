# ruff: noqa: F401,F811
from gaphor import UML
from gaphor.UML.actions.actionseditors import (
    activity_parameter_node_item_editor,
    fork_node_item_editor,
)


def test_activity_parameter_node_item_editor(
    diagram, element_factory, view, event_manager
):
    item = diagram.create(
        UML.actions.ActivityParameterNodeItem,
        subject=element_factory.create(UML.ActivityParameterNode),
    )
    item.subject.parameter = element_factory.create(UML.Parameter)
    view.selection.hovered_item = item
    result = activity_parameter_node_item_editor(item, view, event_manager)

    assert result is True


def test_fork_node_item_editor(diagram, element_factory, view, event_manager):
    item = diagram.create(
        UML.actions.ForkNodeItem, subject=element_factory.create(UML.ForkNode)
    )
    view.selection.hovered_item = item
    result = fork_node_item_editor(item, view, event_manager)

    assert result is False


def test_join_node_item_editor(diagram, element_factory, view, event_manager):
    item = diagram.create(
        UML.actions.ForkNodeItem, subject=element_factory.create(UML.JoinNode)
    )
    view.selection.hovered_item = item
    result = fork_node_item_editor(item, view, event_manager)

    assert result is True
