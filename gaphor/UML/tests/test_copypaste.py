from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.diagram.copypaste import copy_full, paste_full
from gaphor.diagram.tests.test_copypaste_link import two_classes_and_a_generalization
from gaphor.UML.classes import PackageItem


def test_copy_connected_item(diagram, element_factory):
    spc_cls_item, gen_cls_item, gen_item = two_classes_and_a_generalization(
        diagram, element_factory
    )

    buffer = copy_full({spc_cls_item})
    (new_cls_item,) = paste_full(buffer, diagram)

    assert new_cls_item.subject
    assert gen_item.subject.general is gen_cls_item.subject
    assert gen_item.subject.specific is spc_cls_item.subject


def test_full_copy_package_from_owned_diagram(element_factory):
    diagram: Diagram = element_factory.create(Diagram)
    package_item = diagram.create(
        PackageItem, subject=element_factory.create(UML.Package)
    )
    package_item.subject.ownedDiagram = diagram

    copy_buffer = copy_full([package_item], element_factory.lookup)

    new_diagram: Diagram = element_factory.create(Diagram)

    (new_package_item,) = paste_full(copy_buffer, new_diagram)

    assert new_package_item.subject
    assert new_package_item.subject is not package_item.subject


def test_full_copy_package_from_owned_diagram_in_super_package(element_factory):
    diagram: Diagram = element_factory.create(Diagram)
    package_item = diagram.create(
        PackageItem, subject=element_factory.create(UML.Package)
    )
    package_item.subject.ownedDiagram = diagram

    copy_buffer = copy_full([package_item], element_factory.lookup)

    new_diagram: Diagram = element_factory.create(Diagram)
    new_diagram.element = element_factory.create(UML.Package)

    (new_package_item,) = paste_full(copy_buffer, new_diagram)

    assert diagram.owner is package_item.subject
    assert new_package_item.subject
    assert new_package_item.subject is not package_item.subject
    assert new_package_item.subject.owner is new_diagram.owner
