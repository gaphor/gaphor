from gaphor import UML
from gaphor.C4Model.c4model import C4Container
from gaphor.C4Model.diagramitems import C4ContainerItem
from gaphor.C4Model.grouping import ContainerGroup


def container(diagram, element_factory):
    subject = element_factory.create(C4Container)
    return diagram.create(C4ContainerItem, subject=subject)


def test_group_container_can_contain(diagram, element_factory):
    parent = container(diagram, element_factory)
    child = container(diagram, element_factory)

    grouping = ContainerGroup(parent, child)

    assert grouping.can_contain()


def test_group_container_can_group(diagram, element_factory):
    parent = container(diagram, element_factory)
    child = container(diagram, element_factory)

    grouping = ContainerGroup(parent, child)
    grouping.group()

    assert child.subject.namespace is parent.subject


def test_group_container_group_from_package_to_container(diagram, element_factory):
    package = element_factory.create(UML.Package)
    parent = container(diagram, element_factory)
    child = container(diagram, element_factory)

    child.package = package
    grouping = ContainerGroup(parent, child)
    grouping.group()

    assert child.subject.namespace is parent.subject


def test_group_container_ungroup(diagram, element_factory):
    package = element_factory.create(UML.Package)
    diagram.package = package
    parent = container(diagram, element_factory)
    child = container(diagram, element_factory)
    child.subject.package = parent.subject

    grouping = ContainerGroup(parent, child)
    grouping.ungroup()

    assert child.subject.namespace is package
