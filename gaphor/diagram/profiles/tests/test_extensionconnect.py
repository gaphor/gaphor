"""Extension item connection adapter tests."""

from gaphor import UML
from gaphor.diagram.classes.klass import ClassItem
from gaphor.diagram.profiles.extension import ExtensionItem
from gaphor.diagram.tests.fixtures import allow, connect


def test_glue(element_factory, diagram):
    """Test extension item glue."""

    # GIVEN an ExtensionItem, Stereotype, and Class
    ext = diagram.create(ExtensionItem)
    st = diagram.create(ClassItem, subject=element_factory.create(UML.Stereotype))
    cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    # WHEN we try to connect the ExtensionItem tail to the Stereotype
    glued = allow(ext, ext.tail, st)

    # THEN we allow the connection, and we connect them
    assert glued
    connect(ext, ext.tail, st)

    # WHEN we try to connect the ExtensionItem head to the Class
    glued = allow(ext, ext.head, cls)

    # THEN we allow the connection
    assert glued


def test_class_glue(element_factory, diagram):
    """Test extension item gluing to a class."""

    # GIVEN an ExtensionItem and ClassItem
    ext = diagram.create(ExtensionItem)
    cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    # WHEN we try to connect the ExtensionItem tail to a Class
    glued = allow(ext, ext.tail, cls)

    # THEN we don't allow the connection
    assert not glued


def test_stereotype_glue(element_factory, diagram):
    """Test extension item gluing to a stereotype.

    Connecting a Stereotype should work because it is derived from the UML
    Class.
    """

    # GIVEN an ExtensionItem and Stereotype
    ext = diagram.create(ExtensionItem)
    st = diagram.create(ClassItem, subject=element_factory.create(UML.Stereotype))
    assert isinstance(st.subject, UML.Stereotype)

    # WHEN we try to connect the ExtensionItem head to a Stereotype
    glued = allow(ext, ext.head, st)

    # THEN we allow the connection
    assert glued


def test_connection(element_factory, diagram):
    """Test extension item connection."""

    # GIVEN an ExtensionItem, a Stereotype, and a Class
    ext = diagram.create(ExtensionItem)
    st = diagram.create(ClassItem, subject=element_factory.create(UML.Stereotype))
    cls = diagram.create(ClassItem, subject=element_factory.create(UML.Class))

    # WHEN we to connect the ExtensionItem tail to the Stereotype
    # THEN the connection is made
    connect(ext, ext.tail, st)

    # WHEN we to connect the ExtensionItem head to the Class
    # THEN the connection is made
    connect(ext, ext.head, cls)
