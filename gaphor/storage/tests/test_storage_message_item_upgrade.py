from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.storage.storage import load
from gaphor.UML import diagramitems


def test_message_item_upgrade(element_factory, modeling_language, test_models):
    with (test_models / "multiple-messages.gaphor").open(encoding="utf-8") as f:
        load(f, element_factory, modeling_language)

    diagram = element_factory.lselect(Diagram)[0]
    items = [e for e in diagram.get_all_items() if not e.parent]
    message_items = [i for i in items if isinstance(i, diagramitems.MessageItem)]
    subjects = [m.subject for m in message_items]
    messages = element_factory.lselect(UML.Message)
    presentations = [m.presentation for m in messages]

    assert len(messages) == 10
    assert all(subjects), subjects
    assert len(message_items) == 10
    assert all(presentations), presentations
