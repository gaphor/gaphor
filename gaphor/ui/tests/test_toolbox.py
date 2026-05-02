import pytest

from gaphor.core.modeling import Diagram
from gaphor.diagram.diagramtoolbox import get_tool_def, tooliter
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.SysML2 import sysml2
from gaphor.ui.event import CurrentDiagramChanged
from gaphor.ui.toolbox import Toolbox


@pytest.fixture
def modeling_language(event_manager, properties):
    return ModelingLanguageService(event_manager, properties)


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


def test_sysml2_toolbox_definition_contains_sysml2_tools(
    monkeypatch, modeling_language, element_factory
):
    monkeypatch.setenv("GAPHOR_SYSML2", "1")
    modeling_language.select_modeling_language("SysML2")

    tool_ids = {tool.id for tool in tooliter(modeling_language.toolbox_definition)}
    assert "toolbox-sysml2-part-definition" in tool_ids
    assert "toolbox-sysml2-requirement-definition" in tool_ids

    diagram = element_factory.create(Diagram)
    part_tool = get_tool_def(modeling_language, "toolbox-sysml2-part-definition")
    part_item = part_tool.item_factory(diagram, None)
    assert isinstance(part_item.subject, sysml2.PartDefinition)


def test_toolbox_can_select_sysml2_tool(monkeypatch, toolbox, modeling_language):
    monkeypatch.setenv("GAPHOR_SYSML2", "1")
    modeling_language.select_modeling_language("SysML2")

    toolbox.select_tool("toolbox-sysml2-part-definition")

    assert toolbox.active_tool_name == "toolbox-sysml2-part-definition"
