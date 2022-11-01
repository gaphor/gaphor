import pytest

from gaphor.core.modeling import Diagram, ElementFactory
from gaphor.storage.compare import ADD, REMOVE, compare


@pytest.fixture
def current():
    return ElementFactory()


@pytest.fixture
def incoming():
    return ElementFactory()


def test_empty_element_factories(current, incoming):
    change_set = compare(current, incoming)

    assert not change_set.changes


def test_added_element(current, incoming):
    diagram = incoming.create(Diagram)

    change_set = compare(current, incoming)

    change = change_set.changes[0]

    assert len(change_set.changes) == 1
    assert change.type is ADD
    assert change.element_name == "Diagram"
    assert change.element_type == Diagram
    assert change.element_id == diagram.id


def test_removed_element(current, incoming):
    diagram = current.create(Diagram)

    change_set = compare(current, incoming)

    change = change_set.changes[0]

    assert len(change_set.changes) == 1
    assert change.type is REMOVE
    assert change.element_name == "Diagram"
    assert change.element_type == Diagram
    assert change.element_id == diagram.id
