"""Test implementation (interface realization) item connectors."""

from gaphor import UML
from gaphor.UML.classes.interface import InterfaceItem
from gaphor.UML.classes.interfacerealization import InterfaceRealizationItem
from gaphor.UML.classes.klass import ClassItem


def test_non_interface_glue(case):
    """Test non-interface gluing with implementation."""

    impl = case.create(InterfaceRealizationItem)
    clazz = case.create(ClassItem, UML.Class)

    glued = case.allow(impl, impl.head, clazz)
    # connecting head to non-interface item is disallowed
    assert not glued


def test_interface_glue(case):
    """Test interface gluing with implementation."""
    iface = case.create(InterfaceItem, UML.Interface)
    impl = case.create(InterfaceRealizationItem)

    glued = case.allow(impl, impl.head, iface)
    assert glued


def test_classifier_glue(case):
    """Test classifier gluing with implementation."""
    impl = case.create(InterfaceRealizationItem)
    clazz = case.create(ClassItem, UML.Class)

    glued = case.allow(impl, impl.tail, clazz)
    assert glued


def test_connection(case):
    """Test connection of class and interface with implementation."""
    iface = case.create(InterfaceItem, UML.Interface)
    impl = case.create(InterfaceRealizationItem)
    clazz = case.create(ClassItem, UML.Class)

    case.connect(impl, impl.head, iface)
    case.connect(impl, impl.tail, clazz)

    # check the datamodel
    assert isinstance(impl.subject, UML.InterfaceRealization)
    ct = case.get_connected(impl.head)
    assert ct is iface
    assert impl.subject is not None
    assert impl.subject.contract is iface.subject
    assert impl.subject.implementatingClassifier is clazz.subject


def test_reconnection(case):
    """Test reconnection of class and interface with implementation."""
    iface = case.create(InterfaceItem, UML.Interface)
    c1 = case.create(ClassItem, UML.Class)
    c2 = case.create(ClassItem, UML.Class)
    impl = case.create(InterfaceRealizationItem)

    # connect: iface -> c1
    case.connect(impl, impl.head, iface)
    case.connect(impl, impl.tail, c1)

    s = impl.subject

    # reconnect: iface -> c2
    case.connect(impl, impl.tail, c2)

    assert s is not impl.subject
    assert iface.subject is impl.subject.contract
    assert c2.subject is impl.subject.implementatingClassifier
    assert c1.subject is not impl.subject.implementatingClassifier
