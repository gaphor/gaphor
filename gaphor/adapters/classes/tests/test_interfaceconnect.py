"""
Test connections to folded interface.
"""

from gaphor import UML
from gaphor.diagram import items
from gaphor.tests import TestCase

class ImplementationTestCase(TestCase):
    def test_folded_interface_connection(self):
        """Test connecting implementation to folded interface
        """
        iface = self.create(items.InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_PROVIDED
        impl = self.create(items.ImplementationItem)

        assert not impl._solid
        self.connect(impl, impl.head, iface)
        self.assertTrue(impl._solid)


    def test_folded_interface_disconnection(self):
        """Test disconnection implementation from folded interface
        """
        iface = self.create(items.InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_PROVIDED
        impl = self.create(items.ImplementationItem)

        assert not impl._solid
        self.connect(impl, impl.head, iface)
        assert impl._solid

        self.disconnect(impl, impl.head)
        self.assertTrue(not impl._solid)


class DependencyTestCase(TestCase):
    def test_folded_interface_connection(self):
        """Test connecting dependency to folded interface
        """
        iface = self.create(items.InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_PROVIDED
        dep = self.create(items.DependencyItem)

        assert not dep._solid
        self.connect(dep, dep.head, iface)
        self.assertTrue(dep._solid)
        # at the end, interface folded notation shall be `required' one
        self.assertEquals(iface.folded, iface.FOLDED_REQUIRED)


    def test_folded_interface_disconnection(self):
        """Test disconnection dependency from folded interface
        """
        iface = self.create(items.InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_PROVIDED
        dep = self.create(items.DependencyItem)

        assert not dep._solid
        self.connect(dep, dep.head, iface)
        assert dep._solid

        self.disconnect(dep, dep.head)
        self.assertTrue(not dep._solid)
        # after disconnection, interface folded notation shall be `provided' one
        self.assertEquals(iface.folded, iface.FOLDED_PROVIDED)


LINES = (items.ImplementationItem,
        items.GeneralizationItem,
        items.AssociationItem,
        items.IncludeItem,
        items.ExtendItem)

class FoldedInterfaceWithImplementationTestCase(TestCase):
    """
    Test connection of additional diagram lines to folded interface,
    which has already implementation connected.
    """
    def setUp(self):
        super(FoldedInterfaceWithImplementationTestCase, self).setUp()

        self.iface = self.create(items.InterfaceItem, UML.Interface)
        self.iface.folded = self.iface.FOLDED_PROVIDED
        impl = self.create(items.ImplementationItem)

        self.connect(impl, impl.head, self.iface)


    def test_any_line(self):
        """Test glueing different lines to folded interface with implementation
        """
        for cls in LINES:
            line = self.create(cls)
            glued = self.glue(line, line.head, self.iface)
            # no additional lines (specified above) can be glued
            self.assertFalse(glued, 'Glueing of %s should not be allowed' % cls)


    def test_dependency_glue(self):
        """Test glueing dependency to folded interface with implementation
        """
        dep = self.create(items.DependencyItem)
        glued = self.glue(dep, dep.head, self.iface)
        # dependency can be glued...
        self.assertTrue(glued)
        # ... but it cannot be usage dependency
        self.assertFalse(dep.is_usage(self.iface.subject))



class FoldedInterfaceWithDependency(TestCase):
    """
    Test connection of additional diagram lines to folded interface,
    which has already dependency connected.
    """
    def setUp(self):
        super(FoldedInterfaceWithDependency, self).setUp()

        self.iface = self.create(items.InterfaceItem, UML.Interface)
        self.iface.folded = self.iface.FOLDED_PROVIDED
        dep = self.create(items.DependencyItem)

        self.connect(dep, dep.head, self.iface)


    def test_any_line(self):
        """Test glueing different lines to folded interface with dependency
        """
        for cls in LINES:
            line = self.create(cls)
            glued = self.glue(line, line.head, self.iface)
            # no additional lines (specified above) can be glued
            self.assertFalse(glued, 'Glueing of %s should not be allowed' % cls)


    def test_dependency_glue(self):
        """Test glueing dependency to folded interface with dependency
        """
        dep = self.create(items.DependencyItem)
        glued = self.glue(dep, dep.head, self.iface)
        # dependency can be glued...
        self.assertTrue(glued)
        # ... but it cannot be usage dependency
        self.assertFalse(dep.is_usage(self.iface.subject))



# vim:sw=4:et:ai
