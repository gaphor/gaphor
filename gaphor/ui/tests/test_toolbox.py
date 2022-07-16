import pytest

from gaphor.core.modeling import Diagram
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.ui.event import CurrentDiagramChanged
from gaphor.ui.toolbox import Toolbox


@pytest.fixture
def modeling_language(event_manager):
    return ModelingLanguageService(event_manager)


@pytest.fixture
def toolbox(event_manager, properties, modeling_language):
    toolbox = Toolbox(
        event_manager=event_manager,
        properties=properties,
        modeling_language=modeling_language,
    )
    toolbox.open()
    yield toolbox
    toolbox.close()


def test_toolbox_construction(toolbox):
    widget = toolbox.open()

    assert widget


def test_current_tool(toolbox):
    tool_name = toolbox.active_tool_name

    assert tool_name == "toolbox-pointer"


def test_expanded_sections_for_default_diagram(element_factory, toolbox, event_manager):
    diagram = element_factory.create(Diagram)
    event_manager.handle(CurrentDiagramChanged(diagram))

    assert toolbox.expanded_sections() == {
        0: True,
        1: True,
        2: True,
        3: True,
        4: True,
        5: True,
        6: True,
        7: True,
    }


def text_expanded_sections_for_diagram_type(element_factory, toolbox, event_manager):
    diagram = element_factory.create(Diagram)
    diagram.diagramType = "sd"
    event_manager.handle(CurrentDiagramChanged(diagram))

    assert toolbox.expanded_sections() == {
        0: True,
        1: False,
        2: False,
        3: False,
        4: True,
        5: False,
        6: False,
        7: False,
    }


def test_expanded_sections_for_diagram_type_with_custom_settings(
    element_factory, toolbox, event_manager, properties
):
    diagram = element_factory.create(Diagram)
    diagram.diagramType = "sd"
    properties["toolbox-UML-sd-expanded"] = {2: True, 3: True}

    event_manager.handle(CurrentDiagramChanged(diagram))

    assert toolbox.expanded_sections() == {
        0: True,
        1: False,
        2: True,
        3: True,
        4: True,
        5: False,
        6: False,
        7: False,
    }


def test_expanded_sections_switch_from_generic_to_sequence_diagram(
    element_factory, toolbox, event_manager, properties
):
    generic = element_factory.create(Diagram)
    sequence = element_factory.create(Diagram)
    sequence.diagramType = "sd"
    properties["toolbox-UML-sd-expanded"] = {2: True, 3: True}
    event_manager.handle(CurrentDiagramChanged(generic))

    assert toolbox.expanded_sections() == {
        0: True,
        1: True,
        2: True,
        3: True,
        4: True,
        5: True,
        6: True,
        7: True,
    }

    event_manager.handle(CurrentDiagramChanged(sequence))

    assert toolbox.expanded_sections() == {
        0: True,
        1: False,
        2: True,
        3: True,
        4: True,
        5: False,
        6: False,
        7: False,
    }


# test custom expand a column, switch from diagram
def test_expanded_sections_switch_from_generic_to_custom_diagram(
    element_factory, toolbox, event_manager
):
    generic = element_factory.create(Diagram)
    sequence = element_factory.create(Diagram)
    sequence.diagramType = "sd"
    event_manager.handle(CurrentDiagramChanged(generic))

    assert toolbox.expanded_sections() == {
        0: True,
        1: True,
        2: True,
        3: True,
        4: True,
        5: True,
        6: True,
        7: True,
    }

    event_manager.handle(CurrentDiagramChanged(sequence))

    assert toolbox.expanded_sections() == {
        0: True,
        1: False,
        2: False,
        3: False,
        4: True,
        5: False,
        6: False,
        7: False,
    }
