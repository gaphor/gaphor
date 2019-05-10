"""
Test connections to folded interface.
"""

from gaphor import UML
from gaphor.tests import TestCase
from ..implementation import ImplementationItem
from ..interface import InterfaceItem
from ..association import AssociationItem
from ..dependency import DependencyItem
from ..generalization import GeneralizationItem
from gaphor.diagram.general.commentline import CommentLineItem


class ImplementationTestCase(TestCase):
    def test_folded_interface_connection(self):
        """Test connecting implementation to folded interface
        """
        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_PROVIDED
        impl = self.create(ImplementationItem)

        assert not impl._solid
        self.connect(impl, impl.head, iface, iface.ports()[0])
        self.assertTrue(impl._solid)

    def test_folded_interface_disconnection(self):
        """Test disconnection implementation from folded interface
        """
        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_PROVIDED
        impl = self.create(ImplementationItem)

        assert not impl._solid
        self.connect(impl, impl.head, iface, iface.ports()[0])
        assert impl._solid

        self.disconnect(impl, impl.head)
        self.assertTrue(not impl._solid)


class DependencyTestCase(TestCase):
    def test_folded_interface_connection(self):
        """Test connecting dependency to folded interface
        """
        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_PROVIDED
        dep = self.create(DependencyItem)

        assert not dep._solid
        self.connect(dep, dep.head, iface, iface.ports()[0])
        self.assertTrue(dep._solid)
        # at the end, interface folded notation shall be `required' one
        self.assertEqual(iface.folded, iface.FOLDED_REQUIRED)

    def test_folded_interface_disconnection(self):
        """Test disconnection dependency from folded interface
        """
        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_PROVIDED
        dep = self.create(DependencyItem)

        assert not dep._solid
        self.connect(dep, dep.head, iface, iface.ports()[0])
        assert dep._solid

        self.disconnect(dep, dep.head)
        self.assertTrue(not dep._solid)
        # after disconnection, interface folded notation shall be `provided' one
        self.assertEqual(iface.folded, iface.FOLDED_PROVIDED)

    def test_unfolded_interface_disconnection(self):
        """Test disconnection dependency from unfolded interface
        """
        iface = self.create(InterfaceItem, UML.Interface)
        dep = self.create(DependencyItem)

        self.connect(dep, dep.head, iface, iface.ports()[0])
        assert not dep._solid

        self.disconnect(dep, dep.head)
        self.assertTrue(not dep._solid)
        # after disconnection, interface folded property shall be
        # `FOLDED_NONE'
        self.assertEqual(iface.folded, iface.FOLDED_NONE)


LINES = (
    ImplementationItem,
    DependencyItem,
    GeneralizationItem,
    AssociationItem,
    CommentLineItem,
)


class FoldedInterfaceMultipleLinesTestCase(TestCase):
    """
    Test connection of additional diagram lines to folded interface,
    which has already usage dependency or implementation connected.
    """

    def setUp(self):
        super(FoldedInterfaceMultipleLinesTestCase, self).setUp()

        self.iface = self.create(InterfaceItem, UML.Interface)
        self.iface.folded = self.iface.FOLDED_PROVIDED

    def test_interface_with_implementation(self):
        """Test gluing different lines to folded interface with implementation."""

        impl = self.create(ImplementationItem)
        self.connect(impl, impl.head, self.iface, self.iface.ports()[0])

        for cls in LINES:
            line = self.create(cls)
            glued = self.allow(line, line.head, self.iface)
            # no additional lines (specified above) can be glued
            self.assertFalse(glued, "gluing of %s should not be allowed" % cls)

    def test_interface_with_dependency(self):
        """Test gluing different lines to folded interface with dependency."""
        dep = self.create(DependencyItem)
        self.connect(dep, dep.head, self.iface, self.iface.ports()[0])

        for cls in LINES:
            line = self.create(cls)
            glued = self.allow(line, line.head, self.iface)
            # no additional lines (specified above) can be glued
            self.assertFalse(glued, "gluing of %s should not be allowed" % cls)


class FoldedInterfaceSingleLineTestCase(TestCase):
    """
    Test connection of diagram lines to folded interface. Any lines beside
    implementation and dependency should be forbidden to connect.
    """

    def test_interface_with_forbidden_lines(self):
        """Test gluing forbidden lines to folded interface."""

        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_PROVIDED

        for cls in LINES[2:]:
            line = self.create(cls)
            glued = self.allow(line, line.head, iface)
            # no additional lines (specified above) can be glued
            self.assertFalse(glued, "gluing of %s should not be allowed" % cls)
