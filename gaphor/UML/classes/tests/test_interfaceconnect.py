"""Test connections to folded interface."""

from gaphor import UML
from gaphor.core.modeling import StyleSheet
from gaphor.core.modeling.diagram import StyledItem
from gaphor.diagram.tests.fixtures import connect, disconnect
from gaphor.UML.classes.dependency import DependencyItem
from gaphor.UML.classes.interface import Folded, InterfaceItem
from gaphor.UML.classes.interfacerealization import InterfaceRealizationItem
from gaphor.UML.classes.klass import ClassItem


def test_interface_realization_default_line_style(element_factory, diagram):
    element_factory.create(StyleSheet)
    impl = diagram.create(InterfaceRealizationItem)
    style = diagram.style(StyledItem(impl))

    assert style["dash-style"]


def test_interface_realization_folded_interface_connection(element_factory, diagram):
    """Test connecting implementation to folded interface."""
    element_factory.create(StyleSheet)
    iface = diagram.create(InterfaceItem, subject=element_factory.create(UML.Interface))
    iface.folded = Folded.PROVIDED
    impl = diagram.create(InterfaceRealizationItem)

    connect(impl, impl.head, iface)
    diagram.update({iface, impl})

    style = diagram.style(StyledItem(impl))
    assert not style["dash-style"]


def test_interface_realization_folded_interface_disconnection(element_factory, diagram):
    """Test disconnection implementation from folded interface."""
    element_factory.create(StyleSheet)
    iface = diagram.create(InterfaceItem, subject=element_factory.create(UML.Interface))
    iface.folded = Folded.PROVIDED
    impl = diagram.create(InterfaceRealizationItem)

    connect(impl, impl.head, iface)
    disconnect(impl, impl.head)
    impl.request_update()
    style = diagram.style(StyledItem(impl))

    assert style["dash-style"]


def test_dependency_default_line_style(element_factory, diagram):
    element_factory.create(StyleSheet)
    dep = diagram.create(DependencyItem)
    style = diagram.style(StyledItem(dep))

    assert style["dash-style"]


def test_dependency_folded_interface_connection(element_factory, diagram):
    """Test connecting dependency to folded interface."""
    element_factory.create(StyleSheet)
    clazz = diagram.create(ClassItem, subject=element_factory.create(UML.Class))
    iface = diagram.create(InterfaceItem, subject=element_factory.create(UML.Interface))
    iface.folded = Folded.PROVIDED
    dep = diagram.create(DependencyItem)

    connect(dep, dep.head, iface)
    connect(dep, dep.tail, clazz)
    iface.update_shapes()
    diagram.update({clazz, iface, dep})
    style = diagram.style(StyledItem(dep))

    assert dep.subject
    assert not style["dash-style"]
    assert iface.folded == Folded.REQUIRED


def test_dependency_folded_interface_disconnection(element_factory, diagram):
    """Test disconnection dependency from folded interface."""
    element_factory.create(StyleSheet)
    iface = diagram.create(InterfaceItem, subject=element_factory.create(UML.Interface))
    iface.folded = Folded.PROVIDED
    dep = diagram.create(DependencyItem)

    connect(dep, dep.head, iface)
    disconnect(dep, dep.head)
    dep.request_update()
    style = diagram.style(StyledItem(dep))

    assert style["dash-style"]
    assert iface.folded == Folded.PROVIDED


def test_dependency_unfolded_interface_connection(element_factory, diagram):
    """Test disconnection dependency from unfolded interface."""
    element_factory.create(StyleSheet)
    iface = diagram.create(InterfaceItem, subject=element_factory.create(UML.Interface))
    dep = diagram.create(DependencyItem)

    connect(dep, dep.head, iface)
    style = diagram.style(StyledItem(dep))

    assert (7.0, 5.0) == style["dash-style"]
