from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.interactions.interactionspropertypages import MessagePropertyPage


def test_message_property_page(diagram, element_factory):
    item = diagram.create(
        UML.interactions.MessageItem, subject=element_factory.create(UML.Message)
    )
    property_page = MessagePropertyPage(item)

    widget = property_page.construct()
    message_combo = find(widget, "message-combo")
    message_combo.set_active(2)

    assert item.subject.messageSort == "asynchSignal"
