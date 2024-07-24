from gaphor import UML
from gaphor.core.modeling import Diagram, ElementFactory
from gaphor.diagram.copypaste import copy_full, paste_full
from gaphor.diagram.general import DiagramItem
from gaphor.diagram.tests.test_copypaste_link import two_classes_and_a_generalization
from gaphor.UML.classes import ClassItem, GeneralizationItem, PackageItem


def test_copied_item_references_new_model_element(diagram, element_factory):
    cls = element_factory.create(UML.Class)
    cls.name = "Name"
    cls_item = diagram.create(ClassItem, subject=cls)

    buffer = copy_full({cls_item})

    all(paste_full(buffer, diagram))

    assert len(list(diagram.get_all_items())) == 2
    item1, item2 = diagram.get_all_items()

    assert item1.subject
    assert item2.subject
    assert item1.subject in element_factory
    assert item2.subject in element_factory
    assert item1.subject is not item2.subject
    assert item1.subject.name == item2.subject.name


def test_copy_multiple_items(diagram, element_factory):
    cls = element_factory.create(UML.Class)
    cls_item1 = diagram.create(ClassItem, subject=cls)
    cls_item2 = diagram.create(ClassItem, subject=cls)

    buffer = copy_full({cls_item1, cls_item2})

    paste_full(buffer, diagram)

    assert len(list(diagram.get_all_items())) == 4
    assert len(element_factory.lselect(UML.Class)) == 2


def test_copy_items_with_connections(diagram, element_factory):
    spc_cls_item, gen_cls_item, gen_item = two_classes_and_a_generalization(
        diagram, element_factory
    )

    buffer = copy_full({gen_cls_item, gen_item, spc_cls_item})
    new_items = paste_full(buffer, diagram)
    (new_cls1, new_cls2) = (ci.subject for ci in new_items if isinstance(ci, ClassItem))
    (new_gen,) = (gi.subject for gi in new_items if isinstance(gi, GeneralizationItem))

    assert new_gen.general in {new_cls1, new_cls2}
    assert new_gen.specific in {new_cls1, new_cls2}


def test_copy_element_factory(diagram, element_factory):
    """This case tests the boundaries of the copy/paste functionality:

    it copies a complete element factory, something that's not possible
    to do from the UI.
    """
    two_classes_and_a_generalization(diagram, element_factory)

    buffer = copy_full(element_factory)

    new_element_factory = ElementFactory()
    new_diagram = new_element_factory.create(Diagram)
    paste_full(buffer, new_diagram)

    assert len(new_element_factory.lselect(Diagram)) == 1
    assert element_factory.size() == new_element_factory.size()


def test_copy_package_with_diagram(element_factory):
    diagram: Diagram = element_factory.create(Diagram)
    package = element_factory.create(UML.Package)
    package.ownedDiagram = diagram
    package_item = diagram.create(PackageItem, subject=package)

    copy_buffer = copy_full([package_item])
    (new_package_item,) = paste_full(copy_buffer, diagram)
    new_package = new_package_item.subject

    assert diagram in package.ownedDiagram
    assert diagram not in new_package.ownedDiagram
    assert diagram.element is package


def test_shallow_copy_package_with_owned_package(element_factory):
    diagram: Diagram = element_factory.create(Diagram)
    package = element_factory.create(UML.Package)
    subpackage = element_factory.create(UML.Package)
    subpackage.package = package
    package_item = diagram.create(PackageItem, subject=package)

    copy_buffer = copy_full([package_item])
    (new_package_item,) = paste_full(copy_buffer, diagram)
    new_package = new_package_item.subject

    assert subpackage in package.nestedPackage
    assert subpackage.package is package
    assert subpackage not in new_package.nestedPackage


def test_full_copy_package_with_owned_package(element_factory):
    diagram: Diagram = element_factory.create(Diagram)
    package = element_factory.create(UML.Package)
    subpackage = element_factory.create(UML.Package)
    subpackage.package = package
    subpackage.name = "subpackage"
    package_item = diagram.create(PackageItem, subject=package)

    copy_buffer = copy_full([package_item], element_factory.lookup)
    (new_package_item,) = paste_full(copy_buffer, diagram)
    new_package = new_package_item.subject

    assert subpackage in package.nestedPackage
    assert subpackage.package is package
    assert new_package.nestedPackage
    assert subpackage not in new_package.nestedPackage
    assert new_package.nestedPackage[0].name == "subpackage"


def test_copy_diagram_with_elements(diagram, element_factory):
    other_diagram: Diagram = element_factory.create(Diagram)
    two_classes_and_a_generalization(other_diagram, element_factory)

    diagram_item = diagram.create(DiagramItem, subject=other_diagram)

    copy_buffer = copy_full([diagram_item], element_factory.lookup)

    target_diagram: Diagram = element_factory.create(Diagram)
    (new_diagram_item, *_other) = paste_full(copy_buffer, target_diagram)

    new_diagram = new_diagram_item.subject

    assert new_diagram.ownedPresentation
