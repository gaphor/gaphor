from gaphas.selection import Selection

from gaphor import UML
from gaphor.diagram.diagramtoolbox import new_item_factory
from gaphor.diagram.tools import itemtool
from gaphor.diagram.tools.shortcut import delete_selected_items, unselect
from gaphor.UML.diagramitems import PackageItem
from gaphor.diagram.general import CommentItem, CommentLineItem
from gaphor.core.modeling import Comment
from gaphor.diagram.connectors import ItemDisconnected
from gaphor.diagram.tests.fixtures import connect
from gaphor.core import event_handler
from gaphor.diagram.tools.placement import (
    PlacementState,
    on_drag_begin,
    on_drag_end,
    on_drag_update,
    placement_tool,
)
from gaphor.diagram.tools.itemtool import item_tool, on_drag_end as item_tool


class MockView:
    def __init__(self):
        self.selection = Selection()


def test_delete_selected_items(create, diagram, event_manager):
    package_item = create(PackageItem, UML.Package)
    view = MockView()
    view.selection.select_items(package_item)

    delete_selected_items(view, event_manager)

    assert not diagram.ownedPresentation


def test_delete_selected_owner(create, diagram, event_manager):
    package_item = create(PackageItem, UML.Package)
    diagram.element = package_item.subject
    view = MockView()
    view.selection.select_items(package_item)

    delete_selected_items(view, event_manager)

    assert not diagram.ownedPresentation
    assert diagram.element is None


def test_unselect_item_from_drop(create, event_manager, view):
    comment = create(CommentItem, element_class=Comment)
    tool = itemtool.item_tool(event_manager)
    line = create(CommentLineItem)
    connect(line, line.handles()[0], comment)
    view.selection.select_items(line)
    view.add_controller(tool)

    events = []

    @event_handler(ItemDisconnected)
    def handler(e):
        events.append(e)

    event_manager.subscribe(handler)

    itemtool.on_drag_end(tool, 0, 0)

    unselect(view, event_manager)

    assert len(view.selection.selected_items) == 0
    assert not events


def test_cancel_line(create, event_manager, view):
    comment = create(CommentItem, element_class=Comment)
    factory = new_item_factory(CommentLineItem)
    state = PlacementState(factory, event_manager, handle_index=-1)
    tool_placement = placement_tool(factory, event_manager, handle_index=-1)
    view.add_controller(tool_placement)

    on_drag_begin(tool_placement, 2, 1, state)

    tool = itemtool.item_tool(event_manager)
    view.add_controller(tool)

    line = next(iter(view.selection.selected_items))
    connect(line, line.handles()[0], comment)

    events = []

    @event_handler(ItemDisconnected)
    def handler(e):
        events.append(e)

    event_manager.subscribe(handler)

    itemtool.on_drag_end(tool, 3, 2)

    on_drag_update(tool_placement, 1, 1, state)

    on_drag_end(tool_placement, 0, 0, state)

    unselect(view, event_manager)

    assert len(view.selection.selected_items) == 0
    assert events
