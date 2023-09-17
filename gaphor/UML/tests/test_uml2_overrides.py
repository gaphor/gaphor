from gaphor import UML


def test_qualified_name():
    p1 = UML.Package()
    p2 = UML.Package()
    p3 = UML.Package()

    p1.name = "package1"
    p2.name = "package2"
    p3.name = "package3"
    p3.package = p2
    p2.package = p1

    assert p3.qualifiedName == ["package1", "package2", "package3"]


def test_partly_connected_component_required_relation():
    usage = UML.Usage()
    component = UML.Component()

    component.clientDependency = usage

    assert not component.required


def test_component_required_relation():
    usage = UML.Usage()
    component = UML.Component()
    interface = UML.Interface()

    component.clientDependency = usage
    usage.supplier = interface

    assert [interface] == component.required


def test_component_provided_relation():
    realization = UML.InterfaceRealization()
    component = UML.Component()
    interface = UML.Interface()

    component.interfaceRealization = realization
    realization.contract = interface

    assert [interface] == component.provided
