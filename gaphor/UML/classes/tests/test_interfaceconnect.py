"""Test connections to folded interface."""

from gaphor import UML
from gaphor.UML.classes.dependency import DependencyItem
from gaphor.UML.classes.interface import Folded, InterfaceItem
from gaphor.UML.classes.interfacerealization import InterfaceRealizationItem
from gaphor.UML.classes.klass import ClassItem


class TestInterfaceRealization:
    def test_default_line_style(self, case):
        impl = case.create(InterfaceRealizationItem)

        assert impl.style["dash-style"]

    def test_folded_interface_connection(self, case):
        """Test connecting implementation to folded interface."""
        iface = case.create(InterfaceItem, UML.Interface)
        iface.folded = Folded.PROVIDED
        impl = case.create(InterfaceRealizationItem)

        case.connect(impl, impl.head, iface)
        case.diagram.update_now((iface, impl))

        assert not impl.style["dash-style"]

    def test_folded_interface_disconnection(self, case):
        """Test disconnection implementation from folded interface."""
        iface = case.create(InterfaceItem, UML.Interface)
        iface.folded = Folded.PROVIDED
        impl = case.create(InterfaceRealizationItem)

        case.connect(impl, impl.head, iface)
        case.disconnect(impl, impl.head)
        impl.request_update()

        assert impl.style["dash-style"]


class TestDependency:
    def test_default_line_style(self, case):
        dep = case.create(DependencyItem)

        assert dep.style["dash-style"]

    def test_folded_interface_connection(self, case):
        """Test connecting dependency to folded interface."""
        clazz = case.create(ClassItem, UML.Class)
        iface = case.create(InterfaceItem, UML.Interface)
        iface.folded = Folded.PROVIDED
        dep = case.create(DependencyItem)

        case.connect(dep, dep.head, iface)
        case.connect(dep, dep.tail, clazz)
        iface.update_shapes()
        case.diagram.update_now((clazz, iface, dep))

        assert dep.subject
        assert not dep.style["dash-style"]
        assert iface.folded == Folded.REQUIRED

    def test_folded_interface_disconnection(self, case):
        """Test disconnection dependency from folded interface."""
        iface = case.create(InterfaceItem, UML.Interface)
        iface.folded = Folded.PROVIDED
        dep = case.create(DependencyItem)

        case.connect(dep, dep.head, iface)
        case.disconnect(dep, dep.head)
        dep.request_update()

        assert dep.style["dash-style"]
        assert iface.folded == Folded.PROVIDED

    def test_unfolded_interface_connection(self, case):
        """Test disconnection dependency from unfolded interface."""
        iface = case.create(InterfaceItem, UML.Interface)
        dep = case.create(DependencyItem)

        case.connect(dep, dep.head, iface)
        assert (7.0, 5.0) == dep.style["dash-style"]
