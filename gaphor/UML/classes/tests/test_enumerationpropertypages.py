from gaphor import UML
from gaphor.UML.classes.enumerationpropertypages import EnumerationPage


def test_enumeration_property_page(diagram, element_factory):
    item = diagram.create(
        UML.classes.EnumerationItem, subject=element_factory.create(UML.Enumeration)
    )
    property_page = EnumerationPage(item)

    property_page.construct()
