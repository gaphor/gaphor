import pytest

from gaphor.diagram.tests.fixtures import diagram, element_factory, event_manager
from gaphor.services.undomanager import UndoManager


@pytest.fixture
def undo_manager(event_manager):
    return UndoManager(event_manager)
