import pytest

import gaphor.services.componentregistry
import gaphor.ui.menufragment
from gaphor.core.modeling import ElementFactory
from gaphor.plugins.console.consolewindow import ConsoleWindow


class MainWindowStub:
    def __init__(self):
        self.window = None


@pytest.fixture
def component_registry():
    component_registry = gaphor.services.componentregistry.ComponentRegistry()
    component_registry.register("element_factory", ElementFactory())
    return component_registry


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
