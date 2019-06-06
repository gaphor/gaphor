import pytest

from gaphor.ui.consolewindow import ConsoleWindow
import gaphor.services.componentregistry


class MainWindowStub:
    def __init__(self):
        self.window = None


@pytest.fixture
def component_registry():
    return gaphor.services.componentregistry.ComponentRegistry()


@pytest.fixture
def main_window():
    return MainWindowStub()


def test_open_close(component_registry, main_window):
    window = ConsoleWindow(component_registry, main_window)

    window.open()
    window.close()

    assert (
        len(window.action_group.list_actions()) == 2
    ), window.action_group.list_actions()
