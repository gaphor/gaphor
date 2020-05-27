"""
Test connections to folded interface.
"""

from gaphor import UML
from gaphor.tests import TestCase
from gaphor.UML.classes.dependency import DependencyItem
from gaphor.UML.classes.generalization import GeneralizationItem
from gaphor.UML.classes.implementation import ImplementationItem
from gaphor.UML.classes.interface import Folded, InterfaceItem
from gaphor.UML.classes.klass import ClassItem


class ImplementationTestCase(TestCase):
    def test_default_line_style(self):
        impl = self.create(ImplementationItem)

        assert impl.style["dash-style"]

    def test_folded_interface_connection(self):
        """Test connecting implementation to folded interface
        """
        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = Folded.PROVIDED
        impl = self.create(ImplementationItem)

        self.connect(impl, impl.head, iface, iface.ports()[0])

        assert not impl.style["dash-style"]

    def test_folded_interface_disconnection(self):
        """Test disconnection implementation from folded interface
        """
        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = Folded.PROVIDED
        impl = self.create(ImplementationItem)

        self.connect(impl, impl.head, iface, iface.ports()[0])
        self.disconnect(impl, impl.head)
        impl.request_update()

        assert impl.style["dash-style"]


class DependencyTestCase(TestCase):
    def test_default_line_style(self):
        dep = self.create(DependencyItem)

        assert dep.style["dash-style"]

    def test_folded_interface_connection(self):
        """Test connecting dependency to folded interface
        """
        clazz = self.create(ClassItem, UML.Class)
        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = Folded.PROVIDED
        dep = self.create(DependencyItem)

        self.connect(dep, dep.head, iface, iface.ports()[0])
        self.connect(dep, dep.tail, clazz, clazz.ports()[0])
        iface.request_update()
        iface.canvas.update_now()

        assert dep.subject
        assert not dep.style["dash-style"]
        assert iface.folded == Folded.REQUIRED

    def test_folded_interface_disconnection(self):
        """Test disconnection dependency from folded interface
        """
        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = Folded.PROVIDED
        dep = self.create(DependencyItem)

        self.connect(dep, dep.head, iface, iface.ports()[0])
        self.disconnect(dep, dep.head)
        dep.request_update()

        assert dep.style["dash-style"]
        assert iface.folded == Folded.PROVIDED

    def test_unfolded_interface_connection(self):
        """Test disconnection dependency from unfolded interface
        """
        iface = self.create(InterfaceItem, UML.Interface)
        dep = self.create(DependencyItem)

        self.connect(dep, dep.head, iface, iface.ports()[0])
        assert (7.0, 5.0) == dep.style["dash-style"]
