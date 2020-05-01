from gaphor import UML
from gaphor.diagram.tests.fixtures import clear_model, connect, copy_clear_and_paste
from gaphor.UML.classes import AssociationItem, ClassItem, InterfaceItem


def test_class_with_attributes(diagram, element_factory):
    cls = element_factory.create(UML.Class)
    attr = element_factory.create(UML.Property)
    UML.parse(attr, "- attr: str")
    cls.ownedAttribute = attr

    cls_item = diagram.create(ClassItem, subject=cls)

    new_items = copy_clear_and_paste({cls_item}, diagram, element_factory)
    new_cls_item = new_items.pop()

    assert isinstance(new_cls_item, ClassItem)
    assert UML.format(new_cls_item.subject.ownedAttribute[0]) == "- attr: str"


def test_class_with_operation(diagram, element_factory):
    cls = element_factory.create(UML.Class)
    oper = element_factory.create(UML.Operation)
    UML.parse(oper, "- oper(inout param: str): str")
    cls.ownedOperation = oper

    cls_item = diagram.create(ClassItem, subject=cls)

    new_items = copy_clear_and_paste({cls_item}, diagram, element_factory)
    new_cls_item = new_items.pop()

    assert isinstance(new_cls_item, ClassItem)
    assert (
        UML.format(new_cls_item.subject.ownedOperation[0])
        == "- oper(inout param: str): str"
    )


def test_interface_with_attributes_and_operation(diagram, element_factory):
    iface = element_factory.create(UML.Interface)

    attr = element_factory.create(UML.Property)
    UML.parse(attr, "- attr: str")
    iface.ownedAttribute = attr

    oper = element_factory.create(UML.Operation)
    UML.parse(oper, "- oper(inout param: str): str")
    iface.ownedOperation = oper

    iface_item = diagram.create(InterfaceItem, subject=iface)

    new_items = copy_clear_and_paste({iface_item}, diagram, element_factory)
    new_iface_item = new_items.pop()

    assert isinstance(new_iface_item, InterfaceItem)
    assert UML.format(new_iface_item.subject.ownedAttribute[0]) == "- attr: str"
    assert (
        UML.format(new_iface_item.subject.ownedOperation[0])
        == "- oper(inout param: str): str"
    )


def two_classes_and_an_association(diagram, element_factory):
    gen_cls = element_factory.create(UML.Class)
    spc_cls = element_factory.create(UML.Class)
    gen_cls_item = diagram.create(ClassItem, subject=gen_cls)
    spc_cls_item = diagram.create(ClassItem, subject=spc_cls)
    assoc_item = diagram.create(AssociationItem)

    connect(assoc_item, assoc_item.handles()[0], gen_cls_item)
    connect(assoc_item, assoc_item.handles()[1], spc_cls_item)
    UML.model.set_navigability(
        assoc_item.subject, assoc_item.subject.memberEnd[0], True
    )

    return gen_cls_item, spc_cls_item, assoc_item


def test_copy_remove_paste_items_with_connections(diagram, element_factory):
    gen_cls_item, spc_cls_item, assoc_item = two_classes_and_an_association(
        diagram, element_factory
    )

    new_items = copy_clear_and_paste(
        {gen_cls_item, assoc_item, spc_cls_item}, diagram, element_factory
    )
    new_cls1, new_cls2 = element_factory.lselect(lambda e: isinstance(e, UML.Class))
    new_assoc = element_factory.lselect(lambda e: isinstance(e, UML.Association))[0]

    assert new_assoc.memberEnd[0].type in {new_cls1, new_cls2}
    assert new_assoc.memberEnd[1].type in {new_cls1, new_cls2}
    assert new_assoc.memberEnd[0] in new_assoc.memberEnd[1].type.ownedAttribute
    assert new_cls1.presentation[0] in new_items
    assert new_cls2.presentation[0] in new_items
    assert new_assoc.presentation[0] in new_items
