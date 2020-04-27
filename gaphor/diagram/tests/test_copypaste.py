import pytest

from gaphor import UML
from gaphor.diagram.copypaste import copy, paste
from gaphor.diagram.tests.fixtures import connect
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
