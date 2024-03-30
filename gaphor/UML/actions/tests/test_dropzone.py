import pytest
from gaphas.view import GtkView

from gaphor import UML
from gaphor.diagram.painter import ItemPainter
from gaphor.diagram.selection import Selection
from gaphor.UML.actions.action import ActionItem
from gaphor.UML.actions.actionstoolbox import partition_config
from gaphor.UML.actions.dropzone import PartitionDropZoneMoveMixin
from gaphor.UML.actions.partition import PartitionItem


@pytest.fixture
def view(diagram):
    view = GtkView(model=diagram, selection=Selection())
    item_painter = ItemPainter(view.selection)
    view.painter = item_painter
    view.bounding_box_painter = item_painter
    return view


class DropZoneMove(PartitionDropZoneMoveMixin):
    def __init__(self, item, view):
        self.item = item
        self.view = view


def test_drop_on_swimlane_on_first_partition(view, create):
    swimlanes: PartitionItem = create(PartitionItem, UML.ActivityPartition)
    partition_config(swimlanes)
    action = create(ActionItem, UML.Action)

    dropzone = DropZoneMove(action, view)
    dropzone.drop(swimlanes, (10, swimlanes.height / 2))

    assert action.subject in swimlanes.partition[0].node


def test_drop_on_swimlane_on_second_partition(view, create):
    swimlanes: PartitionItem = create(PartitionItem, UML.ActivityPartition)
    partition_config(swimlanes)
    action = create(ActionItem, UML.Action)

    dropzone = DropZoneMove(action, view)
    dropzone.drop(swimlanes, (swimlanes.width - 10, swimlanes.height / 2))

    assert action.subject in swimlanes.partition[1].node


def test_drop_from_first_swimlane_on_second_partition(view, create):
    swimlanes: PartitionItem = create(PartitionItem, UML.ActivityPartition)
    partition_config(swimlanes)
    action = create(ActionItem, UML.Action)

    dropzone = DropZoneMove(action, view)
    handles = swimlanes.handles()
    dropzone.drop(swimlanes, (handles[0].pos.x + 10, swimlanes.height / 2))
    dropzone.drop(swimlanes, (handles[1].pos.x - 10, swimlanes.height / 2))

    assert action.subject not in swimlanes.partition[0].node
    assert action.subject in swimlanes.partition[1].node


def test_drop_from_second_swimlane_to_outside(view, create):
    swimlanes: PartitionItem = create(PartitionItem, UML.ActivityPartition)
    partition_config(swimlanes)
    action = create(ActionItem, UML.Action)

    dropzone = DropZoneMove(action, view)
    handles = swimlanes.handles()
    dropzone.drop(swimlanes, (handles[1].pos.x - 10, swimlanes.height / 2))
    dropzone.drop(swimlanes, (handles[1].pos.x - 10, 1000))

    assert action.subject not in swimlanes.partition[0].node
    assert action.subject not in swimlanes.partition[1].node
