import pytest

from gaphor.ui.elementeditor import ElementEditor


class DiagramsStub:
    def get_current_view(self):
        return None


@pytest.fixture
def diagrams():
    return DiagramsStub()


class DummyProperties(dict):
    def set(self, key, val):
        self[key] = val


def test_reopen_of_window(event_manager, element_factory, diagrams):
    properties = DummyProperties()
    editor = ElementEditor(event_manager, element_factory, diagrams, properties)

    editor.open()
    editor.close()
    editor.open()
    editor.close()
