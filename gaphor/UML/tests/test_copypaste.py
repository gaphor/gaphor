from gaphor.diagram.copypaste import copy, paste_full
from gaphor.diagram.tests.test_copypaste_link import two_classes_and_a_generalization


def test_copy_connected_item(diagram, element_factory):
    spc_cls_item, gen_cls_item, gen_item = two_classes_and_a_generalization(
        diagram, element_factory
    )

    buffer = copy({spc_cls_item})
    (new_cls_item,) = paste_full(buffer, diagram, element_factory.lookup)

    assert new_cls_item.subject
    assert gen_item.subject.general is gen_cls_item.subject
    assert gen_item.subject.specific is spc_cls_item.subject
