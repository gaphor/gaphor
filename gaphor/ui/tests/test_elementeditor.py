import pytest

from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import ElementFactory
from gaphor.ui.elementeditor import ElementEditor
from gaphor.ui.mainwindow import Diagrams


@pytest.fixture
def event_manager():
    return EventManager()


@pytest.fixture
def element_factory(event_manager):
    return ElementFactory(event_manager)


@pytest.fixture
def diagrams(event_manager, element_factory):
    return Diagrams(
        event_manager=event_manager, element_factory=element_factory, properties={}
    )


def test_reopen_of_window(event_manager, element_factory, diagrams):
    editor = ElementEditor(event_manager, element_factory, diagrams)

    editor.open()
    editor.close()
    editor.open()
    editor.close()
