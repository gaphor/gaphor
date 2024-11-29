"""Test connector item connectors."""

from gaphor import UML
from gaphor.diagram.tests.fixtures import allow, connect, disconnect
from gaphor.UML.classes.component import ComponentItem
from gaphor.UML.classes.dependency import DependencyItem
from gaphor.UML.classes.interface import Folded, InterfaceItem, Side
from gaphor.UML.classes.interfacerealization import InterfaceRealizationItem
from gaphor.UML.deployments import ConnectorItem
from gaphor.UML.deployments.connectorconnect import LegacyConnectorConnectBase


def provide(component, interface):
    """Change component's data so it implements interfaces."""
    impl = component.model.create(UML.InterfaceRealization)
    component.interfaceRealization = impl
    impl.contract = interface


def require(component, interface):
    """Change component's data so it requires interface."""
    usage = component.model.create(UML.Usage)
    component.clientDependency = usage
    usage.supplier = interface


def test_glue(create):
    """Test gluing connector to component."""

    component = create(ComponentItem, UML.Component)
    line = create(ConnectorItem)

    glued = allow(line, line.head, component)
    assert glued


def test_component_connection(create):
    """Test connecting connector to a component."""
    component = create(ComponentItem, UML.Component)
    line = create(ConnectorItem)

    connect(line, line.head, component)
    assert line.subject is None


def test_glue_both(create):
    """Test gluing connector to component when one is connected."""

    c1 = create(ComponentItem, UML.Component)
    c2 = create(ComponentItem, UML.Component)
    line = create(ConnectorItem)

    connect(line, line.head, c1)
    glued = allow(line, line.tail, c2)
    assert not glued


def test_non_folded_glue(create):
    """Test non-folded interface gluing."""

    iface = create(InterfaceItem, UML.Component)
    line = create(ConnectorItem)

    glued = allow(line, line.head, iface)
    assert glued


def test_folded_glue(create):
    """Test folded interface gluing."""

    iface = create(InterfaceItem, UML.Component)
    line = create(ConnectorItem)

    iface.folded = Folded.REQUIRED
    glued = allow(line, line.head, iface)
    assert glued


def test_glue_when_dependency_connected(create):
    """Test interface gluing, when dependency connected."""

    iface = create(InterfaceItem, UML.Component)
    dep = create(DependencyItem)
    line = create(ConnectorItem)

    connect(dep, dep.head, iface)

    iface.folded = Folded.REQUIRED
    glued = allow(line, line.head, iface)
    assert glued


def test_glue_when_implementation_connected(create):
    """Test interface gluing, when implementation connected."""

    iface = create(InterfaceItem, UML.Component)
    impl = create(InterfaceRealizationItem)
    line = create(ConnectorItem)

    connect(impl, impl.head, iface)

    iface.folded = Folded.REQUIRED
    glued = allow(line, line.head, iface)
    assert glued


def test_glue_when_connector_connected(create):
    """Test interface gluing, when connector connected."""

    iface = create(InterfaceItem, UML.Interface)
    comp = create(ComponentItem, UML.Component)
    iface.folded = Folded.REQUIRED

    line1 = create(ConnectorItem)
    line2 = create(ConnectorItem)

    connect(line1, line1.tail, comp)
    connect(line1, line1.head, iface)
    assert Folded.PROVIDED == iface.folded

    glued = allow(line2, line2.head, iface)
    assert glued


def test_simple_connection(create, diagram):
    """Test simple connection to an interface."""
    iface = create(InterfaceItem, UML.Interface)
    comp = create(ComponentItem, UML.Component)
    line = create(ConnectorItem)

    connect(line, line.head, iface)
    connect(line, line.tail, comp)
    iface.update_shapes()
    diagram.update({iface, comp, line})

    # interface goes into assembly mode
    assert iface.folded == Folded.PROVIDED
    # no UML metamodel yet
    assert line.subject


def test_simple_disconnection(create):
    """Test disconnection of simple connection to an interface."""
    iface = create(InterfaceItem, UML.Component)
    line = create(ConnectorItem)

    iface.folded = Folded.PROVIDED

    connect(line, line.head, iface)

    disconnect(line, line.head)
    assert Folded.PROVIDED == iface.folded
    assert iface.side == Side.N

    assert all(p.connectable for p in iface.ports())


def test_getting_component(create):
    """Test getting component."""
    conn1 = create(ConnectorItem)
    conn2 = create(ConnectorItem)

    c1 = create(ComponentItem, UML.Component)
    c2 = create(ComponentItem, UML.Component)

    # connect component
    connect(conn1, conn1.tail, c1)
    connect(conn2, conn2.head, c2)

    assert c1 is LegacyConnectorConnectBase.get_component(conn1)
    assert c2 is LegacyConnectorConnectBase.get_component(conn2)


def test_connection(create):
    """Test basic assembly connection."""
    conn1 = create(ConnectorItem)
    conn2 = create(ConnectorItem)

    c1 = create(ComponentItem, UML.Component)
    c2 = create(ComponentItem, UML.Component)

    iface = create(InterfaceItem, UML.Interface)
    iface.folded = Folded.ASSEMBLY

    # first component provides interface
    # and the second one requires it
    provide(c1.subject, iface.subject)
    require(c2.subject, iface.subject)

    # connect component
    connect(conn1, conn1.head, c1)
    connect(conn2, conn2.head, c2)

    # make an assembly
    connect(conn1, conn1.tail, iface)
    connect(conn2, conn2.tail, iface)

    # test UML data model
    assert conn1.subject is conn2.subject, f"{conn1.subject} is not {conn2.subject}"
    assembly = conn1.subject
    assert isinstance(assembly, UML.Connector)
    assert "assembly" == assembly.kind

    # there should be two connector ends
    assert len(assembly.end) == 2


def test_required_port_glue(create):
    """Test if required port gluing works."""

    conn1 = create(ConnectorItem)
    conn2 = create(ConnectorItem)

    c1 = create(ComponentItem, UML.Component)
    c2 = create(ComponentItem, UML.Component)

    iface = create(InterfaceItem, UML.Interface)
    iface.folded = Folded.ASSEMBLY
    rport = iface.ports()[2]

    provide(c1.subject, iface.subject)
    require(c2.subject, iface.subject)

    # connect components
    connect(conn1, conn1.head, c1)
    connect(conn2, conn2.head, c2)

    connect(conn1, conn1.tail, iface)
    glued = allow(conn2, conn2.tail, iface, rport)
    assert glued


def test_connection_order(create):
    """Test connection order of assembly connection."""
    conn1 = create(ConnectorItem)
    conn2 = create(ConnectorItem)

    c1 = create(ComponentItem, UML.Component)
    c2 = create(ComponentItem, UML.Component)

    iface = create(InterfaceItem, UML.Interface)

    # both components provide interface only
    provide(c1.subject, iface.subject)
    provide(c2.subject, iface.subject)

    # connect components
    connect(conn1, conn1.head, c1)
    connect(conn2, conn2.head, c2)

    # connect to provided port
    connect(conn1, conn1.tail, iface)
    connect(conn2, conn2.tail, iface)
    # no UML data model yet (no connection on required port)
    assert conn1.subject
    assert conn2.subject


def test_additional_connections(create):
    """Test additional connections to assembly connection."""
    conn1 = create(ConnectorItem)
    conn2 = create(ConnectorItem)
    conn3 = create(ConnectorItem)

    c1 = create(ComponentItem, UML.Component)
    c2 = create(ComponentItem, UML.Component)
    c3 = create(ComponentItem, UML.Component)

    iface = create(InterfaceItem, UML.Interface)
    iface.folded = Folded.ASSEMBLY

    # provide and require interface by components
    provide(c1.subject, iface.subject)
    require(c2.subject, iface.subject)
    require(c3.subject, iface.subject)

    # connect components
    connect(conn1, conn1.head, c1)
    connect(conn2, conn2.head, c2)
    connect(conn3, conn3.head, c3)

    # create assembly
    connect(conn1, conn1.tail, iface)
    connect(conn2, conn2.tail, iface)

    # test precondition
    assert conn1.subject and conn2.subject

    #  additional connection
    connect(conn3, conn3.tail, iface)

    # test UML data model
    assert conn3.subject is conn1.subject

    assembly = conn1.subject

    assert 3 == len(assembly.end)


def test_disconnection(create, element_factory):
    """Test assembly connector disconnection."""
    conn1 = create(ConnectorItem)
    conn2 = create(ConnectorItem)

    c1 = create(ComponentItem, UML.Component)
    c2 = create(ComponentItem, UML.Component)

    iface = create(InterfaceItem, UML.Interface)
    iface.folded = Folded.ASSEMBLY

    # first component provides interface
    # and the second one requires it
    provide(c1.subject, iface.subject)
    require(c2.subject, iface.subject)

    # connect component
    connect(conn1, conn1.head, c1)
    connect(conn2, conn2.head, c2)

    # make an assembly
    connect(conn1, conn1.tail, iface)
    connect(conn2, conn2.tail, iface)

    # test precondition
    assert conn1.subject is conn2.subject

    disconnect(conn1, conn1.head)

    assert conn1.subject is None
    assert conn2.subject is None

    assert len(element_factory.lselect(UML.Connector)) == 0
    assert len(element_factory.lselect(UML.ConnectorEnd)) == 0
    assert len(element_factory.lselect(UML.Port)) == 0
