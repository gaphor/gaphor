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
    info_item = element_factory.create(UML.Class)
    info_item.name = "IItem"
    property_page = InformationFlowPropertyPage(subject)

    widget = property_page.construct()
    use = find(widget, "use-information-flow")
    use.set_active(True)
    combo = find(widget, "information-flow-combo")
    combo.set_active_id(info_item.id)

    assert subject.informationFlow[0].conveyed[0] is info_item


def test_information_flow_is_loaded(element_factory):
    subject = element_factory.create(UML.Connector)
    property_pages = PropertyPages(subject)

    assert any(isinstance(page, InformationFlowPropertyPage) for page in property_pages)


def test_information_flow_source_and_target(element_factory):
    subject = element_factory.create(UML.Connector)
    head_end = element_factory.create(UML.ConnectorEnd)
    head_end.role = element_factory.create(UML.Property)
    tail_end = element_factory.create(UML.ConnectorEnd)
    tail_end.role = element_factory.create(UML.Property)
    subject.end = head_end
    subject.end = tail_end

    property_page = InformationFlowPropertyPage(subject)

    widget = property_page.construct()
    use = find(widget, "use-information-flow")
    use.set_active(True)

    assert subject.informationFlow[0].informationSource is head_end.role
    assert subject.informationFlow[0].informationTarget is tail_end.role


def test_information_flow_invert_direction(element_factory):
    subject = element_factory.create(UML.Connector)
    head_end = element_factory.create(UML.ConnectorEnd)
    head_end.role = element_factory.create(UML.Property)
    tail_end = element_factory.create(UML.ConnectorEnd)
    tail_end.role = element_factory.create(UML.Property)
    subject.end = head_end
    subject.end = tail_end

    property_page = InformationFlowPropertyPage(subject)

    widget = property_page.construct()
    use = find(widget, "use-information-flow")
    use.set_active(True)

    property_page._invert_direction_changed(None)

    assert subject.informationFlow[0].informationSource is tail_end.role
    assert subject.informationFlow[0].informationTarget is head_end.role
