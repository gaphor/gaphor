import pytest

from gaphor.ui.consolewindow import ConsoleWindow
import gaphor.services.componentregistry
import gaphor.ui.menufragment


class MainWindowStub:
    def __init__(self):
        self.window = None


@pytest.fixture
def component_registry():
    return gaphor.services.componentregistry.ComponentRegistry()


@pytest.fixture
def main_window():
    return MainWindowStub()


@pytest.fixture
def tools_menu():
    return gaphor.ui.menufragment.MenuFragment()


def test_open_close(component_registry, main_window, tools_menu):
    window = ConsoleWindow(component_registry, main_window, tools_menu)

    window.open()
    window.close()

    assert tools_menu.menu.get_n_items() == 1
