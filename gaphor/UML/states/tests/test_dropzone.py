import pytest

from gaphor import UML
from gaphor.core.modeling import StyleSheet
from gaphor.UML.states.dropzone import RegionDropZoneMoveMixin
from gaphor.UML.states.state import StateItem


@pytest.fixture
def parent_state(create, diagram, element_factory, view):
    element_factory.create(StyleSheet)
    parent: StateItem = create(StateItem, UML.State)
    parent.subject.region = element_factory.create(UML.Region)
    parent.subject.region = element_factory.create(UML.Region)
    diagram.update()
    view.update_bounding_box(diagram.ownedPresentation)
    return parent


class DropZoneMove(RegionDropZoneMoveMixin):
    def __init__(self, item, view):
        self.item = item
        self.view = view


def test_drop_state_on_first_region(parent_state, view, create):
    state: StateItem = create(StateItem, UML.State)
    dropzone = DropZoneMove(state, view)

    dropzone.drop(parent_state, (10, parent_state.height / 2))

    assert state.subject.container is parent_state.subject.region[0]


def test_drop_state_on_second_region(parent_state, view, create):
    state: StateItem = create(StateItem, UML.State)
    dropzone = DropZoneMove(state, view)

    dropzone.drop(parent_state, (10, parent_state.height - 10))

    assert state.subject.container is parent_state.subject.region[1]


def test_drop_from_first_region_on_second_region(parent_state, view, create):
    state: StateItem = create(StateItem, UML.State)
    dropzone = DropZoneMove(state, view)

    dropzone.drop(parent_state, (10, parent_state.height / 2))
    dropzone.drop(parent_state, (10, parent_state.height - 10))

    assert state.subject.container is parent_state.subject.region[1]
