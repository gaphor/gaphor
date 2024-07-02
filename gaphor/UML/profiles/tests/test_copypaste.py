from gaphor import UML
from gaphor.diagram.tests.fixtures import (
    connect,
    copy_and_paste_link,
    copy_clear_and_paste_link,
)
from gaphor.UML.classes import ClassItem
from gaphor.UML.profiles.extension import ExtensionItem


def metaclass_stereotype_and_extension(diagram, element_factory):
    m_cls = element_factory.create(UML.Class)
    st_cls = element_factory.create(UML.Stereotype)
    m_cls_item = diagram.create(ClassItem, subject=m_cls)
    st_cls_item = diagram.create(ClassItem, subject=st_cls)
    ext_item = diagram.create(ExtensionItem)
    m_cls.name = "Class"
    st_cls.name = "Stereotype"

    connect(ext_item, ext_item.handles()[0], m_cls_item)
    connect(ext_item, ext_item.handles()[1], st_cls_item)

    return m_cls_item, st_cls_item, ext_item


def test_copy_paste_of_stereotype(diagram, element_factory):
    m_cls_item, st_cls_item, ext_item = metaclass_stereotype_and_extension(
        diagram, element_factory
    )

    copy_and_paste_link({m_cls_item, ext_item, st_cls_item}, diagram, element_factory)

    new_ext_item = ext_item.subject.presentation[1]

    assert new_ext_item.head
    assert new_ext_item.tail


def test_cut_paste_of_stereotype(diagram, element_factory):
    m_cls_item, st_cls_item, ext_item = metaclass_stereotype_and_extension(
        diagram, element_factory
    )

    copy_clear_and_paste_link(
        {m_cls_item, st_cls_item, ext_item}, diagram, element_factory
    )
    new_m_cls = next(element_factory.select(lambda e: e.name == "Class"))
    new_st_cls = next(element_factory.select(lambda e: e.name == "Stereotype"))
    new_ext = next(element_factory.select(UML.Extension))

    assert new_m_cls in new_ext.memberEnd[:].type
    assert new_st_cls in new_ext.memberEnd[:].type
    assert new_st_cls is new_ext.ownedEnd.type
