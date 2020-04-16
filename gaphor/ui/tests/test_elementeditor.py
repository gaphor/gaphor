import pytest

from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import ElementFactory
from gaphor.ui.elementeditor import ElementEditor
from gaphor.UML.modelinglanguage import UMLModelingLanguage


class DiagramsStub:
    def get_current_view(self):
        return None


@pytest.fixture
def diagrams():
    return DiagramsStub()


def test_reopen_of_window(event_manager, element_factory, diagrams):
    editor = ElementEditor(event_manager, element_factory, diagrams)

    editor.open()
    editor.close()
    editor.open()
    editor.close()
