"""
Test implementation (interface realization) item connectors.
"""

from gaphor import UML
from gaphor.tests import TestCase
from gaphor.UML.classes.implementation import ImplementationItem
from gaphor.UML.classes.interface import InterfaceItem
from gaphor.UML.classes.klass import ClassItem


class ImplementationTestCase(TestCase):
    def test_non_interface_glue(self):
        """Test non-interface gluing with implementation."""

        impl = self.create(ImplementationItem)
        clazz = self.create(ClassItem, UML.Class)

        glued = self.allow(impl, impl.head, clazz)
        # connecting head to non-interface item is disallowed
        self.assertFalse(glued)

    def test_interface_glue(self):
        """Test interface gluing with implementation
        """
        iface = self.create(InterfaceItem, UML.Interface)
        impl = self.create(ImplementationItem)

        glued = self.allow(impl, impl.head, iface)
        assert glued

    def test_classifier_glue(self):
        """Test classifier gluing with implementation
        """
        impl = self.create(ImplementationItem)
        clazz = self.create(ClassItem, UML.Class)

        glued = self.allow(impl, impl.tail, clazz)
        assert glued

    def test_connection(self):
        """Test connection of class and interface with implementation
        """
        iface = self.create(InterfaceItem, UML.Interface)
        impl = self.create(ImplementationItem)
        clazz = self.create(ClassItem, UML.Class)

        self.connect(impl, impl.head, iface)
        self.connect(impl, impl.tail, clazz)

        # check the datamodel
        self.assertTrue(isinstance(impl.subject, UML.Implementation))
        ct = self.get_connected(impl.head)
        assert ct is iface
        assert impl.subject is not None
        assert impl.subject.contract[0] is iface.subject
        assert impl.subject.implementatingClassifier[0] is clazz.subject

    def test_reconnection(self):
        """Test reconnection of class and interface with implementation
        """
        iface = self.create(InterfaceItem, UML.Interface)
        c1 = self.create(ClassItem, UML.Class)
        c2 = self.create(ClassItem, UML.Class)
        impl = self.create(ImplementationItem)

        # connect: iface -> c1
        self.connect(impl, impl.head, iface)
        self.connect(impl, impl.tail, c1)

        s = impl.subject

        # reconnect: iface -> c2
        self.connect(impl, impl.tail, c2)

        assert s is impl.subject
        assert len(impl.subject.contract) == 1
        assert len(impl.subject.implementatingClassifier) == 1
        assert iface.subject in impl.subject.contract
        assert c2.subject in impl.subject.implementatingClassifier
        assert (
            c1.subject not in impl.subject.implementatingClassifier
        ), impl.subject.implementatingClassifier
