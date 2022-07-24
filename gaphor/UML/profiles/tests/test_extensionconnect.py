"""Extension item connection adapter tests."""

from gaphor import UML
from gaphor.core.modeling.diagram import Diagram
from gaphor.diagram.tests.fixtures import allow, connect, disconnect
from gaphor.UML.classes import ClassItem, InterfaceItem
from gaphor.UML.profiles.extension import ExtensionItem


def test_glue_head_to_stereotype(element_factory, diagram):
    ext = diagram.create(ExtensionItem)
    st = diagram.create(ClassItem, subject=element_factory.create(UML.Stereotype))

    glued = allow(ext, ext.head, st)

    assert glued


def test_glue_tail_to_stereotype(element_factory, diagram):
    ext = diagram.create(ExtensionItem)
    st = diagram.create(ClassItem, subject=element_factory.create(UML.Stereotype))

    glued = allow(ext, ext.tail, st)

    assert glued


def test_glue_head_to_class(element_factory, diagram):
    ext = diagram.create(ExtensionItem)
    cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    glued = allow(ext, ext.head, cls)

    assert glued


def test_glue_tail_to_class(element_factory, diagram):
    ext = diagram.create(ExtensionItem)
    cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    glued = allow(ext, ext.tail, cls)

    assert not glued


def test_connection(element_factory, diagram):
    ext = diagram.create(ExtensionItem)
    st = diagram.create(ClassItem, subject=element_factory.create(UML.Stereotype))
    cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    connect(ext, ext.tail, st)
    connect(ext, ext.head, cls)

    assert ext.subject
    assert ext.subject.memberEnd[0].type is cls.subject
    assert ext.subject.memberEnd[1].type is st.subject
    assert ext.subject.memberEnd[1] is ext.subject.ownedEnd


def test_connection_namespace(element_factory, diagram):
    pkg = element_factory.create(UML.Package)
    diagram.element = pkg
    ext = diagram.create(ExtensionItem)
    st = diagram.create(ClassItem, subject=element_factory.create(UML.Stereotype))
    cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    connect(ext, ext.tail, st)
    connect(ext, ext.head, cls)

    assert ext.subject.package is pkg


def test_reuse_extension_in_new_diagram(element_factory, diagram):
    ext = diagram.create(ExtensionItem)
    st = diagram.create(ClassItem, subject=element_factory.create(UML.Stereotype))
    cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    connect(ext, ext.tail, st)
    connect(ext, ext.head, cls)

    diagram2 = element_factory.create(Diagram)
    ext2 = diagram2.create(ExtensionItem)
    st2 = diagram2.create(ClassItem, subject=st.subject)
    cls2 = diagram2.create(ClassItem, subject=cls.subject)

    connect(ext2, ext2.tail, st2)
    connect(ext2, ext2.head, cls2)

    assert ext.subject is ext2.subject


def test_disconnect(element_factory, diagram):
    ext = diagram.create(ExtensionItem)
    st = diagram.create(ClassItem, subject=element_factory.create(UML.Stereotype))
    cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    connect(ext, ext.tail, st)
    connect(ext, ext.head, cls)
    subject = ext.subject
    member_end = list(subject.memberEnd)

    disconnect(ext, ext.head)

    assert member_end[0] not in element_factory
    assert member_end[1] not in element_factory
    assert subject not in element_factory


def test_extension_deletion(element_factory, diagram):
    ext = diagram.create(ExtensionItem)
    stereotype = diagram.create(
        ClassItem, subject=element_factory.create(UML.Stereotype)
    )
    metaclass = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    metaclass.subject.name = "Class"
    klass = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    connect(ext, ext.tail, stereotype)
    connect(ext, ext.head, metaclass)

    st_attr = element_factory.create(UML.Property)
    stereotype.subject.ownedAttribute = st_attr

    instspec = UML.recipes.apply_stereotype(klass.subject, stereotype.subject)
    UML.recipes.add_slot(instspec, st_attr)

    assert stereotype.subject in klass.subject.appliedStereotype[:].classifier

    # disconnect indirectly, by deleting the item
    ext.unlink()

    assert not klass.subject.appliedStereotype


def test_extension_deletion_with_2_metaclasses(element_factory, diagram):
    ext = diagram.create(ExtensionItem)
    stereotype = diagram.create(
        ClassItem, subject=element_factory.create(UML.Stereotype)
    )
    metaclass = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    metaclass.subject.name = "Class"
    metaiface = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    metaiface.subject.name = "Interface"

    connect(ext, ext.tail, stereotype)
    connect(ext, ext.head, metaclass)

    UML.recipes.create_extension(metaiface.subject, stereotype.subject)

    # Apply stereotype to class and create slot
    klass = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    iface = diagram.create(InterfaceItem, subject=element_factory.create(UML.Interface))
    UML.recipes.apply_stereotype(klass.subject, stereotype.subject)
    instspec2 = UML.recipes.apply_stereotype(iface.subject, stereotype.subject)

    assert stereotype.subject in klass.subject.appliedStereotype[:].classifier
    assert klass.subject in element_factory

    ext.unlink()

    assert not klass.subject.appliedStereotype
    assert klass.subject in element_factory
    assert [instspec2] == list(iface.subject.appliedStereotype)
