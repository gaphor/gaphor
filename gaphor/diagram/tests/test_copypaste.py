import pytest

from gaphor import UML
from gaphor.diagram.copypaste import copy, paste
from gaphor.UML.classes import ClassItem


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
