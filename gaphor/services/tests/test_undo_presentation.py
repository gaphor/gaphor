"""Test undo, in particular for item specific properties:

* Line: orthogonal, horizontal
* Matrix updates
* Variables
* Solver: add_constraint, remove_constraint
"""
import pytest
from gaphas.connector import Handle

from gaphor.core import Transaction
from gaphor.diagram.presentation import ElementPresentation, LinePresentation
from gaphor.diagram.tests.fixtures import connect
from gaphor.UML import Class
from gaphor.UML.classes import ClassItem, GeneralizationItem


def test_line_orthogonal_property(diagram, undo_manager, event_manager):
    with Transaction(event_manager):
        line = LinePresentation(diagram)
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
        line = LinePresentation(diagram)
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
        line = LinePresentation(diagram)
        line.matrix.translate(10, 0)

    original = tuple(line.matrix)

    with Transaction(event_manager):
        action(line)

    assert tuple(line.matrix) != original

    undo_manager.undo_transaction()

    assert tuple(line.matrix) == original

    undo_manager.redo_transaction()

    assert tuple(line.matrix) != original


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


@pytest.mark.parametrize("index", range(4))
def test_element_handle_position(diagram, undo_manager, event_manager, index):
    with Transaction(event_manager):
        line = diagram.create(ElementPresentation)

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


# TODO: test for insert/remove handle / split segment / merge segment


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
