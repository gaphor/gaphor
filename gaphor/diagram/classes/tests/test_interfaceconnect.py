"""
Test connections to folded interface.
"""

from gaphor import UML
from gaphor.tests import TestCase
from gaphor.diagram.classes.implementation import ImplementationItem
from gaphor.diagram.classes.interface import InterfaceItem
from gaphor.diagram.classes.association import AssociationItem
from gaphor.diagram.classes.dependency import DependencyItem
from gaphor.diagram.classes.generalization import GeneralizationItem
from gaphor.diagram.general.commentline import CommentLineItem


class ImplementationTestCase(TestCase):
    def test_default_line_style(self):
        impl = self.create(ImplementationItem)

        assert impl.style("dash-style")

    def test_folded_interface_connection(self):
        """Test connecting implementation to folded interface
        """
        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_PROVIDED
        impl = self.create(ImplementationItem)

        self.connect(impl, impl.head, iface, iface.ports()[0])

        assert not impl.style("dash-style")

    def test_folded_interface_disconnection(self):
        """Test disconnection implementation from folded interface
        """
        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_PROVIDED
        impl = self.create(ImplementationItem)

        self.connect(impl, impl.head, iface, iface.ports()[0])
        self.disconnect(impl, impl.head)
        impl.request_update()

        assert impl.style("dash-style")


class DependencyTestCase(TestCase):
    def test_default_line_style(self):
        dep = self.create(DependencyItem)

        assert dep.style("dash-style")

    def test_folded_interface_connection(self):
        """Test connecting dependency to folded interface
        """
        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_PROVIDED
        dep = self.create(DependencyItem)

        self.connect(dep, dep.head, iface, iface.ports()[0])

        assert not dep.style("dash-style")
        assert iface.folded == iface.FOLDED_REQUIRED

    def test_folded_interface_disconnection(self):
        """Test disconnection dependency from folded interface
        """
        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_PROVIDED
        dep = self.create(DependencyItem)

        self.connect(dep, dep.head, iface, iface.ports()[0])
        self.disconnect(dep, dep.head)
        dep.request_update()

        assert dep.style("dash-style")
        assert iface.folded == iface.FOLDED_PROVIDED

    def test_unfolded_interface_connection(self):
        """Test disconnection dependency from unfolded interface
        """
        iface = self.create(InterfaceItem, UML.Interface)
        dep = self.create(DependencyItem)

        self.connect(dep, dep.head, iface, iface.ports()[0])
        assert dep.style("dash-style")


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
        super().setUp()

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
            assert not glued, f"gluing of {cls} should not be allowed"

    def test_interface_with_dependency(self):
        """Test gluing different lines to folded interface with dependency."""
        dep = self.create(DependencyItem)
        self.connect(dep, dep.head, self.iface, self.iface.ports()[0])

        for cls in LINES:
            line = self.create(cls)
            glued = self.allow(line, line.head, self.iface)
            # no additional lines (specified above) can be glued
            assert not glued, f"gluing of {cls} should not be allowed"


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
            assert not glued, f"gluing of {cls} should not be allowed"
