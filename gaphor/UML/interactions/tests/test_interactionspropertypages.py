from gaphor import UML
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.interactions.interactionspropertypages import (
    LifelinePropertyPage,
    MessagePropertyPage,
)


def test_lifeline_property_page(diagram, element_factory, event_manager):
    subject = element_factory.create(UML.Lifeline)

    type = element_factory.create(UML.Interface)
    type.name = "Bar"
    property_page = LifelinePropertyPage(subject, event_manager)

    widget = property_page.construct()
    dropdown = find(widget, "element-type")
    bar_index = next(
        n for n, lv in enumerate(dropdown.get_model()) if lv.value == type.id
    )
    dropdown.set_selected(bar_index)

    assert dropdown.get_selected_item().label == "Bar"
    assert subject.represents is type


def test_message_property_page(diagram, element_factory, event_manager):
    item = diagram.create(
        UML.interactions.MessageItem, subject=element_factory.create(UML.Message)
    )
    property_page = MessagePropertyPage(item, event_manager)

    widget = property_page.construct()
    message_combo = find(widget, "message-combo")
    message_combo.set_selected(2)

    assert item.subject.messageSort == "asynchSignal"
