"""Extension item connection adapter tests."""

from gaphor import UML
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.profiles.extension import ExtensionItem
from gaphor.diagram.tests.fixtures import allow, connect


def test_glue(element_factory, diagram):
    """Test extension item glue."""

    ext = diagram.create(ExtensionItem)
    st = diagram.create(ClassItem, subject=element_factory.create(UML.Stereotype))
    cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    glued = allow(ext, ext.tail, st)
    assert glued

    connect(ext, ext.tail, st)

    glued = allow(ext, ext.head, cls)
    assert glued


def test_class_glue(element_factory, diagram):
    """Test extension item gluing to a class."""

    ext = diagram.create(ExtensionItem)
    cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    # cannot connect extension item tail to a class
    glued = allow(ext, ext.tail, cls)
    assert not glued


def test_stereotype_glue(element_factory, diagram):
    """Test extension item gluing to a stereotype."""

    ext = diagram.create(ExtensionItem)
    st = diagram.create(ClassItem, subject=element_factory.create(UML.Stereotype))

    # test precondition
    assert isinstance(st.subject, UML.Stereotype)

    # can connect extension item head to a Stereotype UML metaclass,
    # because it derives from Class UML metaclass
    glued = allow(ext, ext.head, st)
    assert glued


def test_connection(element_factory, diagram):
    """Test extension item connection."""
    ext = diagram.create(ExtensionItem)
    st = diagram.create(ClassItem, subject=element_factory.create(UML.Stereotype))
    cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    connect(ext, ext.tail, st)
    connect(ext, ext.head, cls)
