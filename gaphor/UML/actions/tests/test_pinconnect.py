import pytest

from gaphor import UML
from gaphor.diagram.connectors import Connector
from gaphor.diagram.copypaste import copy_full, paste_link
from gaphor.UML.actions.action import ActionItem
from gaphor.UML.actions.pin import InputPinItem, OutputPinItem
from gaphor.UML.actions.pinconnect import ActionPinConnector


@pytest.fixture
def action_item(diagram, element_factory):
    return diagram.create(ActionItem, subject=element_factory.create(UML.Action))


@pytest.fixture
def input_pin_item(diagram):
    return diagram.create(InputPinItem)


@pytest.fixture
def output_pin_item(diagram):
    return diagram.create(OutputPinItem)


def test_input_pin_can_connect_to_action(action_item, input_pin_item):
    connector = Connector(action_item, input_pin_item)

    assert isinstance(connector, ActionPinConnector)
    assert connector.allow(input_pin_item.handles()[0], action_item.ports()[0])


def test_output_pin_can_connect_to_action(action_item, output_pin_item):
    connector = Connector(action_item, output_pin_item)

    assert isinstance(connector, ActionPinConnector)
    assert connector.allow(output_pin_item.handles()[0], action_item.ports()[0])


def test_connect_input_pin_to_action(action_item, input_pin_item):
    connector = Connector(action_item, input_pin_item)

    connected = connector.connect(input_pin_item.handles()[0], action_item.ports()[0])

    assert connected
    assert input_pin_item.subject
    assert input_pin_item.subject in action_item.subject.inputValue


def test_disconnect_input_pin_to_action(action_item, input_pin_item):
    connector = Connector(action_item, input_pin_item)
    connector.connect(input_pin_item.handles()[0], action_item.ports()[0])

    connector.disconnect(input_pin_item.handles()[0])

    assert input_pin_item.subject is None
    assert input_pin_item.diagram


def test_connect_output_pin_to_action(action_item, output_pin_item):
    connector = Connector(action_item, output_pin_item)

    connected = connector.connect(output_pin_item.handles()[0], action_item.ports()[0])

    assert connected
    assert output_pin_item.subject
    assert output_pin_item.subject in action_item.subject.outputValue


def test_disconnect_output_pin_to_action(action_item, output_pin_item):
    connector = Connector(action_item, output_pin_item)
    connector.connect(output_pin_item.handles()[0], action_item.ports()[0])

    connector.disconnect(output_pin_item.handles()[0])

    assert output_pin_item.subject is None
    assert output_pin_item.diagram


def test_delete_action_leaves_pins_in_place(
    diagram, action_item, input_pin_item, element_factory
):
    connector = Connector(action_item, input_pin_item)
    connector.connect(input_pin_item.handles()[0], action_item.ports()[0])

    copy_data = copy_full({action_item, input_pin_item})

    new_elements = paste_link(copy_data, diagram)

    new_action_item = next(e for e in new_elements if isinstance(e, ActionItem))
    new_input_pin_item = next(e for e in new_elements if isinstance(e, InputPinItem))

    new_action_item.unlink()

    assert new_action_item.diagram is None
    assert not new_action_item.children

    assert action_item in element_factory
    assert input_pin_item in element_factory
    assert new_action_item not in element_factory
    assert new_input_pin_item not in element_factory
