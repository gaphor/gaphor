from gaphor import UML
from gaphor.UML.classes.enumerationpropertypages import (
    EnumerationPage,
    ShowEnumerationPage,
)


def test_enumeration_property_page(element_factory, event_manager):
    subject = element_factory.create(UML.Enumeration)

    property_page = EnumerationPage(subject, event_manager)

    property_page.construct()


def test_show_enumeration_property_page(diagram, element_factory, event_manager):
    item = diagram.create(
        UML.classes.EnumerationItem, subject=element_factory.create(UML.Enumeration)
    )
    property_page = ShowEnumerationPage(item, event_manager)

    property_page.construct()
