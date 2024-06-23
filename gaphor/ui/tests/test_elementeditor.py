import textwrap

import pytest

import gaphor.UML.classes.classespropertypages  # noqa
from gaphor import UML
from gaphor.core.modeling.diagram import StyledItem
from gaphor.diagram.tests.fixtures import find
from gaphor.services.componentregistry import ComponentRegistry
from gaphor.ui.elementeditor import ElementEditor, dump_css_tree
from gaphor.UML.diagramitems import ClassItem, PackageItem


class DiagramsStub:
    def get_current_view(self):
        return None


@pytest.fixture
def diagrams():
    return DiagramsStub()


@pytest.fixture
def component_registry(event_manager):
    reg = ComponentRegistry()
    reg.register("event_manager", event_manager)
    return reg


class DummyProperties(dict):
    def set(self, key, val):
        self[key] = val


def test_reopen_of_window(
    event_manager, component_registry, element_factory, modeling_language, diagrams
):
    properties = DummyProperties()
    editor = ElementEditor(
        event_manager,
        component_registry,
        element_factory,
        modeling_language,
        diagrams,
        properties,
    )

    editor.open()
    editor.close()
    editor.open()
    editor.close()


def test_create_pages(
    event_manager,
    component_registry,
    element_factory,
    modeling_language,
    diagrams,
    create,
):
    properties = DummyProperties()
    editor = ElementEditor(
        event_manager,
        component_registry,
        element_factory,
        modeling_language,
        diagrams,
        properties,
    )
    package_item = create(PackageItem, UML.Package)

    editor.open()
    editor.editors.create_pages(package_item)

    assert find(editor.editors.vbox, "name-editor")

    editor.editors.clear_pages()

    assert not find(editor.editors.vbox, "name-editor")


def test_dump_css_tree(element_factory, create):
    class_item = create(ClassItem, UML.Class)

    class_item.subject.ownedAttribute = element_factory.create(UML.Property)
    class_item.subject.ownedOperation = element_factory.create(UML.Operation)

    text = dump_css_tree(StyledItem(class_item))

    assert text == textwrap.dedent(
        """\
        class
         ├╴compartment
         │  ├╴stereotypes
         │  ├╴name
         │  ╰╴from
         ├╴compartment
         │  ╰╴attribute
         ╰╴compartment
            ╰╴operation"""
    )
