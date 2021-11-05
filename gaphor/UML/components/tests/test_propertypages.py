from gaphor import UML
from gaphor.diagram.propertypages import PropertyPages
from gaphor.diagram.tests.fixtures import find
from gaphor.UML.components.componentspropertypage import InformationFlowPropertyPage


def test_information_flow(element_factory):
    subject = element_factory.create(UML.Connector)
    property_page = InformationFlowPropertyPage(subject)

    widget = property_page.construct()
    use = find(widget, "use-information-flow")
    use.set_active(True)
    assert subject.informationFlow


def test_disable_information_flow(element_factory):
    subject = element_factory.create(UML.Connector)
    property_page = InformationFlowPropertyPage(subject)

    widget = property_page.construct()
    use = find(widget, "use-information-flow")
    use.set_active(True)
    use.set_active(False)

    assert not subject.informationFlow


def test_information_flow_name(element_factory):
    subject = element_factory.create(UML.Connector)
    infoItem = element_factory.create(UML.Class)
    infoItem.name = "IItem"
    property_page = InformationFlowPropertyPage(subject)

    widget = property_page.construct()
    use = find(widget, "use-information-flow")
    use.set_active(True)
    combo = find(widget, "information-flow-combo")
    combo.set_active_id(infoItem.id)

    assert subject.informationFlow[0].conveyed[0] is infoItem


def test_information_flow_is_loaded(element_factory):
    subject = element_factory.create(UML.Connector)
    property_pages = PropertyPages(subject)

    assert any(isinstance(page, InformationFlowPropertyPage) for page in property_pages)
