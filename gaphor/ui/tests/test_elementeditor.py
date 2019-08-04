import pytest

from gaphor.services.eventmanager import EventManager
from gaphor.UML.elementfactory import ElementFactory
from gaphor.ui.mainwindow import MainWindow, Diagrams
from gaphor.ui.elementeditor import ElementEditor


@pytest.fixture
def event_manager():
    return EventManager()


@pytest.fixture
def element_factory(event_manager):
    return ElementFactory(event_manager)


@pytest.fixture
def main_window(event_manager, element_factory):
    class MockMainWindow:
        window = None

        def get_ui_component(self, name):
            assert name == "diagrams"
            return Diagrams(
                event_manager=event_manager,
                element_factory=element_factory,
                action_manager=None,
                properties=lambda a, b: 0,
            )

    return MockMainWindow()


def test_reopen_of_window(event_manager, element_factory, main_window):
    editor = ElementEditor(event_manager, element_factory, main_window)

    editor.open()
    editor.close()
    editor.open()
    editor.close()
