import pytest

from gaphor import UML
from gaphor.core.format import format, parse
from gaphor.diagram.tests.fixtures import (
    connect,
    copy_and_paste_link,
    copy_clear_and_paste_link,
)
from gaphor.UML.classes import (
    AssociationItem,
    ClassItem,
    DataTypeItem,
    EnumerationItem,
    InterfaceItem,
)


@pytest.mark.parametrize(
    "cls_type,item",
    [
        (UML.Class, ClassItem),
        (UML.DataType, DataTypeItem),
        (UML.Enumeration, EnumerationItem),
    ],
)
def test_class_with_attributes(diagram, element_factory, cls_type, item):
    cls = element_factory.create(cls_type)
    attr = element_factory.create(UML.Property)
    parse(attr, "- attr: str")
    cls.ownedAttribute = attr

    cls_item = diagram.create(item, subject=cls)

    new_items = copy_clear_and_paste_link({cls_item}, diagram, element_factory)
    new_cls_item = new_items.pop()

    assert isinstance(new_cls_item, item)
    assert format(new_cls_item.subject.ownedAttribute[0]) == "- attr: str"


@pytest.mark.parametrize(
    "cls_type,item",
    [
        (UML.Class, ClassItem),
        (UML.DataType, DataTypeItem),
        (UML.Enumeration, EnumerationItem),
    ],
)
def test_class_with_operation(diagram, element_factory, cls_type, item):
    cls = element_factory.create(cls_type)
    oper = element_factory.create(UML.Operation)
    parse(oper, "- oper(inout param: str): str")
    cls.ownedOperation = oper

    cls_item = diagram.create(item, subject=cls)

    new_items = copy_clear_and_paste_link({cls_item}, diagram, element_factory)
    new_cls_item = new_items.pop()

    assert isinstance(new_cls_item, item)
    assert (
        format(new_cls_item.subject.ownedOperation[0])
        == "- oper(inout param: str): str"
    )


def test_enumeration_with_literal(diagram, element_factory):
    enum = element_factory.create(UML.Enumeration)
    literal = element_factory.create(UML.EnumerationLiteral)
    parse(literal, "apple")
    enum.ownedLiteral = literal

    enum_item = diagram.create(EnumerationItem, subject=enum)

    new_items = copy_clear_and_paste_link({enum_item}, diagram, element_factory)
    new_enum_item = new_items.pop()

    assert isinstance(new_enum_item, EnumerationItem)
    assert format(new_enum_item.subject.ownedLiteral[0]) == "apple"


def test_interface_with_attributes_and_operation(diagram, element_factory):
    iface = element_factory.create(UML.Interface)

    attr = element_factory.create(UML.Property)
    parse(attr, "- attr: str")
    iface.ownedAttribute = attr

    oper = element_factory.create(UML.Operation)
    parse(oper, "- oper(inout param: str): str")
    iface.ownedOperation = oper

    iface_item = diagram.create(InterfaceItem, subject=iface)

    new_items = copy_clear_and_paste_link({iface_item}, diagram, element_factory)
    new_iface_item = new_items.pop()

    assert isinstance(new_iface_item, InterfaceItem)
    assert format(new_iface_item.subject.ownedAttribute[0]) == "- attr: str"
    assert (
        format(new_iface_item.subject.ownedOperation[0])
        == "- oper(inout param: str): str"
    )


def two_classes_and_an_association(diagram, element_factory):
    gen_cls = element_factory.create(UML.Class)
    spc_cls = element_factory.create(UML.Class)
    gen_cls_item = diagram.create(ClassItem, subject=gen_cls)
    spc_cls_item = diagram.create(ClassItem, subject=spc_cls)
    assoc_item = diagram.create(AssociationItem)
    gen_cls.name = "Gen"
    spc_cls.name = "Spc"

    connect(assoc_item, assoc_item.handles()[0], spc_cls_item)
    connect(assoc_item, assoc_item.handles()[1], gen_cls_item)
    UML.recipes.set_navigability(
        assoc_item.subject, assoc_item.subject.memberEnd[0], True
    )

    assert (
        assoc_item.subject.memberEnd[0]
        in assoc_item.subject.memberEnd[1].type.ownedAttribute
    )
    # assert gen_cls_item.ownedAttribute

    return gen_cls_item, spc_cls_item, assoc_item


def test_copy_paste_items_with_connections(diagram, element_factory):
    gen_cls_item, spc_cls_item, assoc_item = two_classes_and_an_association(
        diagram, element_factory
    )

    assert assoc_item.head_subject
    assert assoc_item.tail_subject

    assoc = assoc_item.subject

    copy_and_paste_link(
        {gen_cls_item, assoc_item, spc_cls_item}, diagram, element_factory
    )

    new_assoc_item = assoc.presentation[1]

    assert assoc.presentation[0] is assoc_item

    assert new_assoc_item.head_subject
    assert new_assoc_item.tail_subject


def test_copy_remove_paste_items_with_connections(diagram, element_factory):
    gen_cls_item, spc_cls_item, assoc_item = two_classes_and_an_association(
        diagram, element_factory
    )

    new_items = copy_clear_and_paste_link(
        {gen_cls_item, assoc_item, spc_cls_item}, diagram, element_factory
    )
    new_cls1 = next(
        element_factory.select(
            lambda e: isinstance(e, UML.NamedElement) and e.name == "Gen"
        )
    )
    new_cls2 = next(
        element_factory.select(
            lambda e: isinstance(e, UML.NamedElement) and e.name == "Spc"
        )
    )
    new_assoc = next(element_factory.select(UML.Association))

    assert new_assoc.memberEnd[0].type is new_cls2
    assert new_assoc.memberEnd[1].type is new_cls1
    assert new_assoc.memberEnd[0] in new_assoc.memberEnd[1].type.ownedAttribute
    assert new_cls1.presentation[0] in new_items
    assert new_cls2.presentation[0] in new_items
    assert new_assoc.presentation[0] in new_items
    assert new_assoc.presentation[0].head_subject
    assert new_assoc.presentation[0].tail_subject
