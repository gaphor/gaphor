import pytest

from gaphor import UML
from gaphor.diagram.copypaste import copy, paste
from gaphor.diagram.tests.fixtures import clear_model, connect, copy_clear_and_paste
from gaphor.UML.classes import ClassItem, GeneralizationItem


def test_copy_item_adds_new_item_to_the_diagram(diagram, element_factory):
    cls = element_factory.create(UML.Class)
    cls_item = diagram.create(ClassItem, subject=cls)

    buffer = copy(cls_item)

    paste(buffer, diagram, element_factory.lookup)

    assert len(diagram.canvas.get_root_items()) == 2


def test_copied_item_references_same_model_element(diagram, element_factory):
    cls = element_factory.create(UML.Class)
    cls_item = diagram.create(ClassItem, subject=cls)

    buffer = copy(cls_item)

    paste(buffer, diagram, element_factory.lookup)

    assert len(diagram.canvas.get_root_items()) == 2
    item1, item2 = diagram.canvas.get_root_items()

    assert item1.subject is item2.subject


def test_copy_multiple_items(diagram, element_factory):
    cls = element_factory.create(UML.Class)
    cls_item1 = diagram.create(ClassItem, subject=cls)
    cls_item2 = diagram.create(ClassItem, subject=cls)

    buffer = copy({cls_item1, cls_item2})

    paste(buffer, diagram, element_factory.lookup)

    assert len(diagram.canvas.get_root_items()) == 4
    assert len(element_factory.lselect(lambda e: isinstance(e, UML.Class))) == 1


def test_copy_item_without_copying_connection(diagram, element_factory):
    cls = element_factory.create(UML.Class)
    cls_item = diagram.create(ClassItem, subject=cls)
    gen_item = diagram.create(GeneralizationItem)
    connect(gen_item, gen_item.handles()[0], cls_item)

    buffer = copy({cls_item})

    new_items = paste(buffer, diagram, element_factory.lookup)

    assert len(diagram.canvas.get_root_items()) == 3
    assert len(element_factory.lselect(lambda e: isinstance(e, UML.Class))) == 1
    assert type(new_items) is set
    assert len(new_items) == 1


def two_classes_and_a_generalization(diagram, element_factory):
    gen_cls = element_factory.create(UML.Class)
    spc_cls = element_factory.create(UML.Class)
    gen_cls_item = diagram.create(ClassItem, subject=gen_cls)
    spc_cls_item = diagram.create(ClassItem, subject=spc_cls)
    gen_item = diagram.create(GeneralizationItem)
    connect(gen_item, gen_item.handles()[0], gen_cls_item)
    connect(gen_item, gen_item.handles()[1], spc_cls_item)

    return gen_cls_item, spc_cls_item, gen_item


def test_copy_item_with_connection(diagram, element_factory):
    gen_cls_item, spc_cls_item, gen_item = two_classes_and_a_generalization(
        diagram, element_factory
    )
    buffer = copy({gen_cls_item, gen_item, spc_cls_item})

    new_items = paste(buffer, diagram, element_factory.lookup)
    new_gen_item = next(i for i in new_items if isinstance(i, GeneralizationItem))

    new_cls_item1 = new_gen_item.canvas.get_connection(
        new_gen_item.handles()[0]
    ).connected
    new_cls_item2 = new_gen_item.canvas.get_connection(
        new_gen_item.handles()[1]
    ).connected

    assert new_cls_item1 in diagram.canvas.get_root_items()
    assert new_cls_item2 in diagram.canvas.get_root_items()

    assert len(new_items) == 3
    assert new_cls_item1 in new_items
    assert new_cls_item2 in new_items

    # Model elements are not copied
    assert len(element_factory.lselect(lambda e: isinstance(e, UML.Class))) == 2
    assert (
        len(element_factory.lselect(lambda e: isinstance(e, UML.Generalization))) == 1
    )


def test_copy_item_when_subject_has_been_removed(diagram, element_factory):
    package = element_factory.create(UML.Package)
    cls = element_factory.create(UML.Class)
    cls.package = package
    orig_cls_id = cls.id
    cls_item = diagram.create(ClassItem, subject=cls)

    buffer = copy({cls_item})

    cls_item.unlink()
    cls.unlink()  # normally handled by the sanitizer service

    assert len(diagram.canvas.get_all_items()) == 0
    assert len(element_factory.lselect()) == 2
    assert not element_factory.lookup(orig_cls_id)

    print(buffer)

    paste(buffer, diagram, element_factory.lookup)
    new_cls = element_factory.lselect(lambda e: isinstance(e, UML.Class))[0]
    assert len(diagram.canvas.get_root_items()) == 1
    assert new_cls.package is package
    assert element_factory.lookup(orig_cls_id) is new_cls


def test_copy_remove_paste_items_with_connections(diagram, element_factory):
    gen_cls_item, spc_cls_item, gen_item = two_classes_and_a_generalization(
        diagram, element_factory
    )

    new_items = copy_clear_and_paste(
        {gen_cls_item, gen_item, spc_cls_item}, diagram, element_factory
    )
    new_cls1, new_cls2 = element_factory.lselect(lambda e: isinstance(e, UML.Class))
    new_gen = element_factory.lselect(lambda e: isinstance(e, UML.Generalization))[0]

    assert new_gen.general in {new_cls1, new_cls2}
    assert new_gen.specific in {new_cls1, new_cls2}
    assert new_cls1.presentation[0] in new_items
    assert new_cls2.presentation[0] in new_items
    assert new_gen.presentation[0] in new_items


# copy/paste non-presentation element
