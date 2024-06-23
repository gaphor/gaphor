from gaphor import C4Model
from gaphor.C4Model.propertypages import DescriptionPropertyPage, TechnologyPropertyPage
from gaphor.diagram.tests.fixtures import find


def test_description_property_page(event_manager, element_factory):
    subject = element_factory.create(C4Model.c4model.C4Container)
    property_page = DescriptionPropertyPage(subject, event_manager)

    widget = property_page.construct()
    description = find(widget, "description")
    description.get_buffer().set_text("test")

    assert subject.description == "test"


def test_technology_property_page(event_manager, element_factory):
    subject = element_factory.create(C4Model.c4model.C4Container)
    property_page = TechnologyPropertyPage(subject, event_manager)

    widget = property_page.construct()
    technology = find(widget, "technology")
    technology.set_text("test")

    assert subject.technology == "test"
