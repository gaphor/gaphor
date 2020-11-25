import pytest

from gaphor import UML
from gaphor.application import distribution
from gaphor.storage.parser import parse
from gaphor.storage.storage import load_elements
from gaphor.UML import diagramitems


def test_message_item_upgrade(element_factory, modeling_language):
    """"""
    path = distribution().locate_file("test-models/multiple-messages.gaphor")

    elements = parse(path)
    load_elements(elements, element_factory, modeling_language)

    diagram = element_factory.lselect(UML.Diagram)[0]
    items = diagram.canvas.get_root_items()
    message_items = [i for i in items if isinstance(i, diagramitems.MessageItem)]
    subjects = [m.subject for m in message_items]
    messages = element_factory.lselect(UML.Message)
    presentations = [m.presentation for m in messages]

    assert len(messages) == 10
    assert all(subjects), subjects
    assert len(message_items) == 10
    assert all(presentations), presentations


@pytest.mark.xfail
def test_partition_item_upgrade(element_factory, modeling_language):
    """Test upgrade to version 2.1.0.

    Previous versions had subpartitions nested within a main partition, version
    2.1.0 removed the nesting.
    """
    path = distribution().locate_file("test-models/partition-upgrade.gaphor")

    elements = parse(path)
    load_elements(elements, element_factory, modeling_language)

    diagram = element_factory.lselect(UML.Diagram)[0]
    items = diagram.canvas.get_all_items()
    partitions_items = [i for i in items if isinstance(i, diagramitems.PartitionItem)]
    assert len(partitions_items) == 1

    action_items = [i for i in items if isinstance(i, diagramitems.ActionItem)]
    assert len(action_items) == 1
