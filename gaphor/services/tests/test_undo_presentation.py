"""Test undo, in particular for item specific properties:

* Line: orthogonal, horizontal
* Matrix updates
* Variables
* Solver: add_constraint, remove_constraint
"""

import pytest
from gaphas.connector import Handle
from gaphas.segment import Segment

from gaphor.core import Transaction
from gaphor.diagram.presentation import ElementPresentation, LinePresentation
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML import Class
from gaphor.UML.classes import ClassItem, GeneralizationItem


def test_line_create(diagram, undo_manager, event_manager):
    with Transaction(event_manager):
        diagram.create(LinePresentation)

    assert diagram.ownedPresentation

    undo_manager.undo_transaction()

    assert not diagram.ownedPresentation

    undo_manager.redo_transaction()

    assert diagram.ownedPresentation


def test_line_delete(diagram, undo_manager, event_manager):
    with Transaction(event_manager):
        line = diagram.create(LinePresentation)
        line.insert_handle(1, Handle((20, 20)))
        line.matrix.translate(10, 10)

    with Transaction(event_manager):
        line.unlink()

    undo_manager.undo_transaction()

    line = diagram.ownedPresentation[0]
    assert len(line.handles()) == 3
    assert line.handles()[1].pos.tuple() == (20, 20)
    assert line.matrix.tuple() == (1, 0, 0, 1, 10, 10)


def test_line_orthogonal_property(diagram, undo_manager, event_manager):
    with Transaction(event_manager):
        line = diagram.create(LinePresentation)
        line.insert_handle(0, Handle())

    with Transaction(event_manager):
        line.orthogonal = True

    assert line.orthogonal

    undo_manager.undo_transaction()

    assert not line.orthogonal

    undo_manager.redo_transaction()

    assert line.orthogonal


def test_line_horizontal_property(diagram, undo_manager, event_manager):
    with Transaction(event_manager):
        line = diagram.create(LinePresentation)
        line.insert_handle(0, Handle())

    with Transaction(event_manager):
        line.horizontal = True

    assert line.horizontal

    undo_manager.undo_transaction()

    assert not line.horizontal

    undo_manager.redo_transaction()

    assert line.horizontal


@pytest.mark.parametrize(
    "action",
    [
        lambda line: line.matrix.translate(10, 10),
        lambda line: line.matrix.rotate(1),
        lambda line: line.matrix.scale(2.5, 3.5),
        lambda line: line.matrix.invert(),
    ],
)
def test_matrix_operation(action, diagram, undo_manager, event_manager):
    with Transaction(event_manager):
        line = diagram.create(LinePresentation)
        line.matrix.translate(10, 0)

    original = tuple(line.matrix)

    with Transaction(event_manager):
        action(line)

    assert tuple(line.matrix) != original

    undo_manager.undo_transaction()

    assert tuple(line.matrix) == original

    undo_manager.redo_transaction()

    assert tuple(line.matrix) != original


@pytest.mark.parametrize("index", range(4))
def test_element_handle_position(diagram, undo_manager, event_manager, index):
    with Transaction(event_manager):
        element = diagram.create(ElementPresentation)

    handle = element.handles()[index]
    old_pos = handle.pos.tuple()
    new_pos = (30, 40)

    with Transaction(event_manager):
        handle.pos = new_pos

    assert tuple(handle.pos) == new_pos

    undo_manager.undo_transaction()

    assert handle.pos.tuple() == old_pos

    undo_manager.redo_transaction()

    assert tuple(handle.pos) == new_pos


@pytest.mark.parametrize("index", range(2))
def test_line_handle_position(diagram, undo_manager, event_manager, index):
    with Transaction(event_manager):
        line = diagram.create(LinePresentation)

    handle = line.handles()[index]
    old_pos = handle.pos.tuple()
    new_pos = (30, 40)

    with Transaction(event_manager):
        handle.pos = new_pos

    assert tuple(handle.pos) == new_pos

    undo_manager.undo_transaction()

    assert handle.pos.tuple() == old_pos

    undo_manager.redo_transaction()

    assert tuple(handle.pos) == new_pos


def test_line_handle_on_inserted_handle(diagram, undo_manager, event_manager):
    with Transaction(event_manager):
        line = diagram.create(LinePresentation)

    handle = Handle()
    line.insert_handle(1, handle)

    old_pos = handle.pos.tuple()
    new_pos = (30, 40)

    with Transaction(event_manager):
        handle.pos = new_pos

    assert tuple(handle.pos) == new_pos

    undo_manager.undo_transaction()

    assert handle.pos.tuple() == old_pos

    undo_manager.redo_transaction()

    assert tuple(handle.pos) == new_pos


def test_line_handle_no_events_for_removed_handle(diagram, undo_manager, event_manager):
    with Transaction(event_manager):
        line = diagram.create(LinePresentation)

    handle = Handle()
    line.insert_handle(1, handle)
    line.remove_handle(handle)

    new_pos = (30, 40)

    with Transaction(event_manager):
        handle.pos = new_pos

    assert tuple(handle.pos) == new_pos

    undo_manager.undo_transaction()

    assert handle.pos.tuple() == new_pos


def test_line_loading_of_points(diagram, undo_manager, event_manager, element_factory):
    with Transaction(event_manager):
        line = diagram.create(LinePresentation)
        line.load("points", "[(0, 0), (5, 5), (10, 10)]")
        assert len(line.handles()) == 3

    handle = line.handles()[1]
    old_pos = handle.pos.tuple()
    new_pos = (30, 40)

    with Transaction(event_manager):
        handle.pos = new_pos

    assert tuple(handle.pos) == new_pos

    undo_manager.undo_transaction()

    assert handle.pos.tuple() == old_pos

    undo_manager.redo_transaction()

    assert tuple(handle.pos) == new_pos


def test_line_connections(diagram, undo_manager, element_factory, event_manager):
    with Transaction(event_manager):
        class_item = diagram.create(ClassItem, subject=element_factory.create(Class))
        gen_item = diagram.create(GeneralizationItem)

    handle = gen_item.handles()[0]

    with Transaction(event_manager):
        connect(gen_item, handle, class_item)

    connections = diagram.connections

    assert connections.get_connection(handle)

    undo_manager.undo_transaction()

    assert not connections.get_connection(handle)

    undo_manager.redo_transaction()

    assert connections.get_connection(handle)


def test_line_split_segment(diagram, undo_manager, event_manager):
    with Transaction(event_manager):
        line = diagram.create(LinePresentation)

    head_handle = line.head
    tail_handle = line.tail

    with Transaction(event_manager):
        segment = Segment(line, diagram)
        segment.split((5, 5))

    assert len(line.handles()) == 3

    undo_manager.undo_transaction()

    assert len(line.handles()) == 2
    assert line.head is head_handle
    assert line.tail is tail_handle

    undo_manager.redo_transaction()

    assert len(line.handles()) == 3


def test_line_merge_segment(diagram, undo_manager, event_manager):
    with Transaction(event_manager):
        line = diagram.create(LinePresentation)
        segment = Segment(line, diagram)
        segment.split((5, 5))

    head_handle = line.head
    tail_handle = line.tail

    with Transaction(event_manager):
        segment = Segment(line, diagram)
        segment.merge_segment(0)

    assert len(line.handles()) == 2
    assert line.head is head_handle
    assert line.tail is tail_handle

    undo_manager.undo_transaction()

    assert len(line.handles()) == 3
    assert line.head is head_handle
    assert line.tail is tail_handle

    undo_manager.redo_transaction()

    assert len(line.handles()) == 2


def test_undo_nested_element(diagram, undo_manager, event_manager):
    with Transaction(event_manager):
        parent = diagram.create(ElementPresentation)
        child = diagram.create(ElementPresentation)
        child.change_parent(parent)
        child.matrix.translate(100, 100)
        parent.matrix.translate(100, 100)

    with Transaction(event_manager):
        parent.unlink()

    undo_manager.undo_transaction()

    new_parent, new_child = diagram.ownedPresentation

    assert new_child.parent is new_parent
    assert tuple(new_parent.matrix_i2c) == (1.0, 0, 0, 1, 100, 100)
    assert tuple(new_child.matrix_i2c) == (1.0, 0, 0, 1, 200, 200)
