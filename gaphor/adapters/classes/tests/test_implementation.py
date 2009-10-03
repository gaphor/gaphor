"""
Test implementation (interface realization) item connectors.
"""

from gaphor import UML
from gaphor.diagram import items
from gaphor.tests import TestCase

class ImplementationTestCase(TestCase):
    def test_non_interface_glue(self):
        """Test non-interface glueing with implementation
        """
        impl = self.create(items.ImplementationItem)
        clazz = self.create(items.ClassItem, UML.Class)

        glued = self.glue(impl, impl.head, clazz)
        # connecting head to non-interface item is disallowed
        self.assertFalse(glued)


    def test_interface_glue(self):
        """Test interface glueing with implementation
        """
        iface = self.create(items.InterfaceItem, UML.Interface)
        impl = self.create(items.ImplementationItem)

        glued = self.glue(impl, impl.head, iface)
        self.assertTrue(glued)


    def test_classifier_glue(self):
        """Test classifier glueing with implementation
        """
        impl = self.create(items.ImplementationItem)
        clazz = self.create(items.ClassItem, UML.Class)

        glued = self.glue(impl, impl.tail, clazz)
        self.assertTrue(glued)


    def test_connection(self):
        """Test connection of class and interface with implementation
        """
        iface = self.create(items.InterfaceItem, UML.Interface)
        impl = self.create(items.ImplementationItem)
        clazz = self.create(items.ClassItem, UML.Class)

        self.connect(impl, impl.head, iface)
        self.connect(impl, impl.tail, clazz)

        # check the datamodel
        self.assertTrue(isinstance(impl.subject, UML.Implementation))
        ct = self.get_connected_to_item(impl, impl.head)
        self.assertTrue(ct is iface)
        self.assertTrue(impl.subject is not None)
        self.assertTrue(impl.subject.contract[0] is iface.subject)
        self.assertTrue(impl.subject.implementatingClassifier[0] is clazz.subject)



# vim:sw=4:et:ai
