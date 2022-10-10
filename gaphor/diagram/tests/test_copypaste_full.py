from gaphor import UML
from gaphor.core.modeling import Diagram, ElementFactory
from gaphor.diagram.copypaste import copy, paste_full
from gaphor.diagram.tests.test_copypaste_link import two_classes_and_a_generalization
from gaphor.UML.classes import ClassItem, GeneralizationItem, PackageItem


def test_copied_item_references_new_model_element(diagram, element_factory):
    cls = element_factory.create(UML.Class)
    cls.name = "Name"
    cls_item = diagram.create(ClassItem, subject=cls)

    buffer = copy({cls_item})

    all(paste_full(buffer, diagram, element_factory.lookup))

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

    buffer = copy({cls_item1, cls_item2})

    paste_full(buffer, diagram, element_factory.lookup)

    assert len(list(diagram.get_all_items())) == 4
    assert len(element_factory.lselect(UML.Class)) == 2


def test_copy_items_with_connections(diagram, element_factory):
    spc_cls_item, gen_cls_item, gen_item = two_classes_and_a_generalization(
        diagram, element_factory
    )

    buffer = copy({gen_cls_item, gen_item, spc_cls_item})
    new_items = paste_full(buffer, diagram, element_factory.lookup)
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

    buffer = copy(element_factory)

    new_element_factory = ElementFactory()
    new_diagram = new_element_factory.create(Diagram)
    paste_full(buffer, new_diagram, new_element_factory.lookup)

    # new element factory has one more diagram:
    assert len(new_element_factory.lselect(Diagram)) == 2
    assert element_factory.size() == new_element_factory.size() - 1


def test_copy_package_with_diagram(element_factory):
    diagram: Diagram = element_factory.create(Diagram)
    package = element_factory.create(UML.Package)
    package.ownedDiagram = diagram
    package_item = diagram.create(PackageItem, subject=package)

    copy_buffer = copy([package_item])
    (new_package_item,) = paste_full(copy_buffer, diagram, element_factory.lookup)
    new_package = new_package_item.subject

    assert diagram in package.ownedDiagram
    assert diagram not in new_package.ownedDiagram
    assert diagram.element is package


def test_copy_package_with_owned_package(element_factory):
    diagram: Diagram = element_factory.create(Diagram)
    package = element_factory.create(UML.Package)
    subpackage = element_factory.create(UML.Package)
    subpackage.package = package
    package_item = diagram.create(PackageItem, subject=package)

    copy_buffer = copy([package_item])
    (new_package_item,) = paste_full(copy_buffer, diagram, element_factory.lookup)
    new_package = new_package_item.subject

    assert subpackage in package.nestedPackage
    assert subpackage.package is package
    assert subpackage not in new_package.nestedPackage
