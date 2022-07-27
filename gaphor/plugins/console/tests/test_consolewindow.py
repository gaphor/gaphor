import pytest
from gi.repository import GLib, Gtk

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
    def on_activate(app):
        def auto_close():
            window.close()
            app.quit()

        window = ConsoleWindow(component_registry, main_window, tools_menu)
        window.open()
        app.add_window(window)

        idle = GLib.Idle(GLib.PRIORITY_LOW)
        idle.set_callback(auto_close)
        idle.attach()

    app = Gtk.Application(application_id="org.gaphor.tests.Console")
    app.connect("activate", on_activate)
    app.run()

    assert tools_menu.menu.get_n_items() == 1
