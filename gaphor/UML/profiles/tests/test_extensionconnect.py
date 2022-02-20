"""Extension item connection adapter tests."""

from gaphor import UML
from gaphor.core.modeling.diagram import Diagram
from gaphor.diagram.tests.fixtures import allow, connect
from gaphor.UML.classes.klass import ClassItem
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
