import pytest

from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.ui.elementeditor import ElementEditor
from gaphor.UML.diagramitems import PackageItem
import gaphor.UML.classes.classespropertypages  # noqa


class DiagramsStub:
    def get_current_view(self):
        return None


@pytest.fixture
def diagrams():
    return DiagramsStub()


class DummyProperties(dict):
    def set(self, key, val):
        self[key] = val


def test_reopen_of_window(event_manager, element_factory, modeling_language, diagrams):
    properties = DummyProperties()
    editor = ElementEditor(
        event_manager, element_factory, modeling_language, diagrams, properties
    )

    editor.open()
    editor.close()
    editor.open()
    editor.close()


def test_create_pages(
    event_manager, element_factory, modeling_language, diagrams, create
):
    properties = DummyProperties()
    editor = ElementEditor(
        event_manager, element_factory, modeling_language, diagrams, properties
    )
    package_item = create(PackageItem, UML.Package)

    editor.open()
    editor.editors.create_pages(package_item)

    assert find(editor.editors.vbox, "name-editor")

    editor.editors.clear_pages()

    assert not find(editor.editors.vbox, "name-editor")
