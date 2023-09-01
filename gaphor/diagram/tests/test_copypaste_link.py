from gaphor import UML
from gaphor.core.modeling import Diagram
from gaphor.diagram.copypaste import copy, copy_full, paste, paste_link
from gaphor.diagram.general.simpleitem import Box, Ellipse, Line
from gaphor.diagram.tests.fixtures import connect, copy_clear_and_paste_link
from gaphor.UML.classes import ClassItem, GeneralizationItem


def test_copy_item_adds_new_item_to_the_diagram(diagram, element_factory):
    cls = element_factory.create(UML.Class)
    cls_item = diagram.create(ClassItem, subject=cls)

    _, buffer = next(copy(cls_item))

    paster = paste(buffer, diagram, element_factory.lookup)
    next(paster)
    next(paster, None)
    assert len(list(diagram.get_all_items())) == 2


def test_copied_item_references_same_model_element(diagram, element_factory):
    cls = element_factory.create(UML.Class)
    cls_item = diagram.create(ClassItem, subject=cls)

    _, buffer = next(copy(cls_item))

    all(paste(buffer, diagram, element_factory.lookup))

    assert len(list(diagram.get_all_items())) == 2
    item1, item2 = diagram.get_all_items()

    assert item1.subject is item2.subject


def test_copy_multiple_items(diagram, element_factory):
    cls = element_factory.create(UML.Class)
    cls_item1 = diagram.create(ClassItem, subject=cls)
    cls_item2 = diagram.create(ClassItem, subject=cls)

    buffer = copy_full({cls_item1, cls_item2})

    paste_link(buffer, diagram)

    assert len(list(diagram.get_all_items())) == 4
    assert len(element_factory.lselect(UML.Class)) == 1


def test_copy_item_without_copying_connection(diagram, element_factory):
    cls = element_factory.create(UML.Class)
    cls_item = diagram.create(ClassItem, subject=cls)
    gen_item = diagram.create(GeneralizationItem)
    connect(gen_item, gen_item.handles()[0], cls_item)

    buffer = copy_full({cls_item})

    new_items = paste_link(buffer, diagram)

    assert len(list(diagram.get_all_items())) == 3
    assert len(element_factory.lselect(UML.Class)) == 1
    assert isinstance(new_items, set)
    assert len(new_items) == 1


def two_classes_and_a_generalization(diagram, element_factory):
    gen_cls = element_factory.create(UML.Class)
    spc_cls = element_factory.create(UML.Class)
    gen_cls_item = diagram.create(ClassItem, subject=gen_cls)
    spc_cls_item = diagram.create(ClassItem, subject=spc_cls)
    gen_item = diagram.create(GeneralizationItem)
    connect(gen_item, gen_item.head, gen_cls_item)
    connect(gen_item, gen_item.tail, spc_cls_item)

    return gen_cls_item, spc_cls_item, gen_item


def test_copy_item_with_connection(diagram, element_factory):
    gen_cls_item, spc_cls_item, gen_item = two_classes_and_a_generalization(
        diagram, element_factory
    )
    buffer = copy_full({gen_cls_item, gen_item, spc_cls_item})

    new_items = paste_link(buffer, diagram)
    new_gen_item = next(i for i in new_items if isinstance(i, GeneralizationItem))

    new_cls_item1 = diagram.connections.get_connection(
        new_gen_item.handles()[0]
    ).connected
    new_cls_item2 = diagram.connections.get_connection(
        new_gen_item.handles()[1]
    ).connected

    assert new_cls_item1 in diagram.get_all_items()
    assert new_cls_item2 in diagram.get_all_items()

    assert len(new_items) == 3
    assert new_cls_item1 in new_items
    assert new_cls_item2 in new_items

    # Model elements are not copied
    assert new_cls_item1.subject is gen_cls_item.subject
    assert new_cls_item2.subject is spc_cls_item.subject
    assert new_gen_item.subject is gen_item.subject


def test_copy_item_when_subject_has_been_removed(diagram, element_factory):
    package = element_factory.create(UML.Package)
    cls = element_factory.create(UML.Class)
    cls.package = package
    orig_cls_id = cls.id
    cls_item = diagram.create(ClassItem, subject=cls)

    buffer = copy_full({cls_item})

    cls_item.unlink()
    cls.unlink()  # normally handled by the sanitizer service

    assert set(diagram.ownedPresentation) == set(diagram.get_all_items())
    assert not list(diagram.get_all_items())
    assert cls not in element_factory.select()
    assert not element_factory.lookup(orig_cls_id)

    paste_link(buffer, diagram)
    new_cls = element_factory.lselect(UML.Class)[0]
    (new_cls_item,) = diagram.get_all_items()
    assert new_cls.package is package
    assert new_cls_item.subject is new_cls


def test_copy_remove_paste_items_with_connections(diagram, element_factory):
    gen_cls_item, spc_cls_item, gen_item = two_classes_and_a_generalization(
        diagram, element_factory
    )

    new_items = copy_clear_and_paste_link(
        {gen_cls_item, gen_item, spc_cls_item}, diagram, element_factory
    )
    new_cls1, new_cls2 = element_factory.lselect(UML.Class)
    new_gen = element_factory.lselect(UML.Generalization)[0]

    assert new_gen.general in {new_cls1, new_cls2}
    assert new_gen.specific in {new_cls1, new_cls2}
    assert new_cls1.presentation[0] in new_items
    assert new_cls2.presentation[0] in new_items
    assert new_gen.presentation[0] in new_items


def test_copy_remove_paste_items_when_namespace_is_removed(diagram, element_factory):
    package = element_factory.create(UML.Package)
    cls = element_factory.create(UML.Class)
    cls.package = package
    cls_item = diagram.create(ClassItem, subject=cls)

    diagram_package = element_factory.create(UML.Package)
    diagram.element = diagram_package

    copy_clear_and_paste_link(
        {cls_item}, diagram, element_factory, retain=[diagram_package]
    )

    new_cls = element_factory.lselect(UML.Class)[0]

    assert new_cls.namespace is diagram_package


def test_copy_remove_paste_simple_items(diagram, element_factory):
    box = diagram.create(Box)
    ellipse = diagram.create(Ellipse)
    line = diagram.create(Line)

    new_items = copy_clear_and_paste_link(
        {box, ellipse, line}, diagram, element_factory
    )

    new_box = next(item for item in new_items if isinstance(item, Box))

    assert new_box


def test_copy_to_new_diagram(diagram, element_factory):
    new_diagram = element_factory.create(Diagram)
    cls = element_factory.create(UML.Class)
    cls_item = diagram.create(ClassItem, subject=cls)

    buffer = copy_full({cls_item})

    paste_link(buffer, new_diagram)

    assert len(list(new_diagram.get_all_items())) == 1
    assert next(new_diagram.get_all_items()).diagram is new_diagram
