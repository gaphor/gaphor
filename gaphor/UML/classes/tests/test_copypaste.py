from gaphor import UML
from gaphor.diagram.copypaste import copy, paste
from gaphor.diagram.tests.fixtures import clear_model, connect
from gaphor.UML.classes import AssociationItem, ClassItem


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

    buffer = copy({gen_cls_item, assoc_item, spc_cls_item})

    clear_model(diagram, element_factory)

    print(buffer)

    new_items = paste(buffer, diagram, element_factory.lookup)
    new_cls1, new_cls2 = element_factory.lselect(lambda e: isinstance(e, UML.Class))
    new_assoc = element_factory.lselect(lambda e: isinstance(e, UML.Association))[0]

    assert new_assoc.memberEnd[0].type in {new_cls1, new_cls2}
    assert new_assoc.memberEnd[1].type in {new_cls1, new_cls2}
    assert new_assoc.memberEnd[0] in new_assoc.memberEnd[1].type.ownedAttribute
    assert new_cls1.presentation[0] in new_items
    assert new_cls2.presentation[0] in new_items
    assert new_assoc.presentation[0] in new_items
