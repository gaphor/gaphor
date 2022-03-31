"""Test implementation (interface realization) item connectors."""

from gaphor import UML
from gaphor.diagram.tests.fixtures import allow, connect, get_connected
from gaphor.UML.classes.interface import InterfaceItem
from gaphor.UML.classes.interfacerealization import InterfaceRealizationItem
from gaphor.UML.classes.klass import ClassItem


def test_non_interface_glue(create):
    """Test non-interface gluing with implementation."""

    impl = create(InterfaceRealizationItem)
    clazz = create(ClassItem, UML.Class)

    glued = allow(impl, impl.head, clazz)
    # connecting head to non-interface item is disallowed
    assert not glued


def test_interface_glue(create):
    """Test interface gluing with implementation."""
    iface = create(InterfaceItem, UML.Interface)
    impl = create(InterfaceRealizationItem)

    glued = allow(impl, impl.head, iface)
    assert glued


def test_classifier_glue(create):
    """Test classifier gluing with implementation."""
    impl = create(InterfaceRealizationItem)
    clazz = create(ClassItem, UML.Class)

    glued = allow(impl, impl.tail, clazz)
    assert glued


def test_connection(create):
    """Test connection of class and interface with implementation."""
    iface = create(InterfaceItem, UML.Interface)
    impl = create(InterfaceRealizationItem)
    clazz = create(ClassItem, UML.Class)

    connect(impl, impl.head, iface)
    connect(impl, impl.tail, clazz)

    # check the datamodel
    assert isinstance(impl.subject, UML.InterfaceRealization)
    ct = get_connected(impl, impl.head)
    assert ct is iface
    assert impl.subject is not None
    assert impl.subject.contract is iface.subject
    assert impl.subject.implementatingClassifier is clazz.subject


def test_reconnection(create):
    """Test reconnection of class and interface with implementation."""
    iface = create(InterfaceItem, UML.Interface)
    c1 = create(ClassItem, UML.Class)
    c2 = create(ClassItem, UML.Class)
    impl = create(InterfaceRealizationItem)

    # connect: iface -> c1
    connect(impl, impl.head, iface)
    connect(impl, impl.tail, c1)

    s = impl.subject

    # reconnect: iface -> c2
    connect(impl, impl.tail, c2)

    assert s is not impl.subject
    assert iface.subject is impl.subject.contract
    assert c2.subject is impl.subject.implementatingClassifier
    assert c1.subject is not impl.subject.implementatingClassifier
