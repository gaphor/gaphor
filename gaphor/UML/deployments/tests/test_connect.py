"""Test connector item connectors."""

import pytest

from gaphor import UML
from gaphor.conftest import Case
from gaphor.UML.classes.component import ComponentItem
from gaphor.UML.classes.dependency import DependencyItem
from gaphor.UML.classes.interface import Folded, InterfaceItem, Side
from gaphor.UML.classes.interfacerealization import InterfaceRealizationItem
from gaphor.UML.deployments import ConnectorItem
from gaphor.UML.deployments.connectorconnect import LegacyConnectorConnectBase


class TestComponentConnect:
    """Test connection of connector item to a component."""

    def test_glue(self, case):
        """Test gluing connector to component."""

        component = case.create(ComponentItem, UML.Component)
        line = case.create(ConnectorItem)

        glued = case.allow(line, line.head, component)
        assert glued

    def test_connection(self, case):
        """Test connecting connector to a component."""
        component = case.create(ComponentItem, UML.Component)
        line = case.create(ConnectorItem)

        case.connect(line, line.head, component)
        assert line.subject is None

    def test_glue_both(self, case):
        """Test gluing connector to component when one is connected."""

        c1 = case.create(ComponentItem, UML.Component)
        c2 = case.create(ComponentItem, UML.Component)
        line = case.create(ConnectorItem)

        case.connect(line, line.head, c1)
        glued = case.allow(line, line.tail, c2)
        assert not glued


class TestInterfaceConnect:
    """Test connection with interface acting as assembly connector."""

    def test_non_folded_glue(self, case):
        """Test non-folded interface gluing."""

        iface = case.create(InterfaceItem, UML.Component)
        line = case.create(ConnectorItem)

        glued = case.allow(line, line.head, iface)
        assert glued

    def test_folded_glue(self, case):
        """Test folded interface gluing."""

        iface = case.create(InterfaceItem, UML.Component)
        line = case.create(ConnectorItem)

        iface.folded = Folded.REQUIRED
        glued = case.allow(line, line.head, iface)
        assert glued

    def test_glue_when_dependency_connected(self, case):
        """Test interface gluing, when dependency connected."""

        iface = case.create(InterfaceItem, UML.Component)
        dep = case.create(DependencyItem)
        line = case.create(ConnectorItem)

        case.connect(dep, dep.head, iface)

        iface.folded = Folded.REQUIRED
        glued = case.allow(line, line.head, iface)
        assert glued

    def test_glue_when_implementation_connected(self, case):
        """Test interface gluing, when implementation connected."""

        iface = case.create(InterfaceItem, UML.Component)
        impl = case.create(InterfaceRealizationItem)
        line = case.create(ConnectorItem)

        case.connect(impl, impl.head, iface)

        iface.folded = Folded.REQUIRED
        glued = case.allow(line, line.head, iface)
        assert glued

    def test_glue_when_connector_connected(self, case):
        """Test interface gluing, when connector connected."""

        iface = case.create(InterfaceItem, UML.Interface)
        comp = case.create(ComponentItem, UML.Component)
        iface.folded = Folded.REQUIRED

        line1 = case.create(ConnectorItem)
        line2 = case.create(ConnectorItem)

        case.connect(line1, line1.tail, comp)
        case.connect(line1, line1.head, iface)
        assert Folded.PROVIDED == iface.folded

        glued = case.allow(line2, line2.head, iface)
        assert glued

    def test_simple_connection(self, case):
        """Test simple connection to an interface."""
        iface = case.create(InterfaceItem, UML.Interface)
        comp = case.create(ComponentItem, UML.Component)
        line = case.create(ConnectorItem)

        case.connect(line, line.head, iface)
        case.connect(line, line.tail, comp)
        iface.update_shapes()
        case.diagram.update_now((iface, comp, line))

        # interface goes into assembly mode
        assert iface.folded == Folded.PROVIDED
        # no UML metamodel yet
        assert line.subject

    def test_simple_disconnection(self, case):
        """Test disconnection of simple connection to an interface."""
        iface = case.create(InterfaceItem, UML.Component)
        line = case.create(ConnectorItem)

        iface.folded = Folded.PROVIDED

        case.connect(line, line.head, iface)

        case.disconnect(line, line.head)
        assert Folded.PROVIDED == iface.folded
        assert iface.side == Side.N

        assert all(p.connectable for p in iface.ports())


class AssemblyConnectorCase(Case):
    def create_interfaces(self, *args):
        """Generate interfaces with names specified by arguments.

        :Parameters:
         args
            List of interface names.
        """
        for name in args:
            interface = self.element_factory.create(UML.Interface)
            interface.name = name
            yield interface

    def provide(self, component, interface):
        """Change component's data so it implements interfaces."""
        impl = self.element_factory.create(UML.InterfaceRealization)
        component.interfaceRealization = impl
        impl.contract = interface

    def require(self, component, interface):
        """Change component's data so it requires interface."""
        usage = self.element_factory.create(UML.Usage)
        component.clientDependency = usage
        usage.supplier = interface


class TestAssemblyConnector:
    """Test assembly connector.

    It is assumed that interface and component connection tests defined
    above are working correctly.
    """

    @pytest.fixture
    def case(self):
        case = AssemblyConnectorCase()
        yield case
        case.shutdown()

    def test_getting_component(self, case):
        """Test getting component."""
        conn1 = case.create(ConnectorItem)
        conn2 = case.create(ConnectorItem)

        c1 = case.create(ComponentItem, UML.Component)
        c2 = case.create(ComponentItem, UML.Component)

        # connect component
        case.connect(conn1, conn1.tail, c1)
        case.connect(conn2, conn2.head, c2)

        assert c1 is LegacyConnectorConnectBase.get_component(conn1)
        assert c2 is LegacyConnectorConnectBase.get_component(conn2)

    def test_connection(self, case):
        """Test basic assembly connection."""
        conn1 = case.create(ConnectorItem)
        conn2 = case.create(ConnectorItem)

        c1 = case.create(ComponentItem, UML.Component)
        c2 = case.create(ComponentItem, UML.Component)

        iface = case.create(InterfaceItem, UML.Interface)
        iface.folded = Folded.ASSEMBLY

        # first component provides interface
        # and the second one requires it
        case.provide(c1.subject, iface.subject)
        case.require(c2.subject, iface.subject)

        # connect component
        case.connect(conn1, conn1.head, c1)
        case.connect(conn2, conn2.head, c2)

        # make an assembly
        case.connect(conn1, conn1.tail, iface)
        case.connect(conn2, conn2.tail, iface)

        # test UML data model
        assert conn1.subject is conn2.subject, f"{conn1.subject} is not {conn2.subject}"
        assembly = conn1.subject
        assert isinstance(assembly, UML.Connector)
        assert "assembly" == assembly.kind

        # there should be two connector ends
        assert len(assembly.end) == 2

    def test_required_port_glue(self, case):
        """Test if required port gluing works."""

        conn1 = case.create(ConnectorItem)
        conn2 = case.create(ConnectorItem)

        c1 = case.create(ComponentItem, UML.Component)
        c2 = case.create(ComponentItem, UML.Component)

        iface = case.create(InterfaceItem, UML.Interface)
        iface.folded = Folded.ASSEMBLY
        rport = iface.ports()[2]

        case.provide(c1.subject, iface.subject)
        case.require(c2.subject, iface.subject)

        # connect components
        case.connect(conn1, conn1.head, c1)
        case.connect(conn2, conn2.head, c2)

        case.connect(conn1, conn1.tail, iface)
        glued = case.allow(conn2, conn2.tail, iface, rport)
        assert glued

    def test_connection_order(self, case):
        """Test connection order of assembly connection."""
        conn1 = case.create(ConnectorItem)
        conn2 = case.create(ConnectorItem)

        c1 = case.create(ComponentItem, UML.Component)
        c2 = case.create(ComponentItem, UML.Component)

        iface = case.create(InterfaceItem, UML.Interface)

        # both components provide interface only
        case.provide(c1.subject, iface.subject)
        case.provide(c2.subject, iface.subject)

        # connect components
        case.connect(conn1, conn1.head, c1)
        case.connect(conn2, conn2.head, c2)

        # connect to provided port
        case.connect(conn1, conn1.tail, iface)
        case.connect(conn2, conn2.tail, iface)
        # no UML data model yet (no connection on required port)
        assert conn1.subject
        assert conn2.subject

    def test_addtional_connections(self, case):
        """Test additional connections to assembly connection."""
        conn1 = case.create(ConnectorItem)
        conn2 = case.create(ConnectorItem)
        conn3 = case.create(ConnectorItem)

        c1 = case.create(ComponentItem, UML.Component)
        c2 = case.create(ComponentItem, UML.Component)
        c3 = case.create(ComponentItem, UML.Component)

        iface = case.create(InterfaceItem, UML.Interface)
        iface.folded = Folded.ASSEMBLY

        # provide and require interface by components
        case.provide(c1.subject, iface.subject)
        case.require(c2.subject, iface.subject)
        case.require(c3.subject, iface.subject)

        # connect components
        case.connect(conn1, conn1.head, c1)
        case.connect(conn2, conn2.head, c2)
        case.connect(conn3, conn3.head, c3)

        # create assembly
        case.connect(conn1, conn1.tail, iface)
        case.connect(conn2, conn2.tail, iface)

        # test precondition
        assert conn1.subject and conn2.subject

        #  additional connection
        case.connect(conn3, conn3.tail, iface)

        # test UML data model
        assert conn3.subject is conn1.subject

        assembly = conn1.subject

        assert 3 == len(assembly.end)

    def test_disconnection(self, case):
        """Test assembly connector disconnection."""
        conn1 = case.create(ConnectorItem)
        conn2 = case.create(ConnectorItem)

        c1 = case.create(ComponentItem, UML.Component)
        c2 = case.create(ComponentItem, UML.Component)

        iface = case.create(InterfaceItem, UML.Interface)
        iface.folded = Folded.ASSEMBLY

        # first component provides interface
        # and the second one requires it
        case.provide(c1.subject, iface.subject)
        case.require(c2.subject, iface.subject)

        # connect component
        case.connect(conn1, conn1.head, c1)
        case.connect(conn2, conn2.head, c2)

        # make an assembly
        case.connect(conn1, conn1.tail, iface)
        case.connect(conn2, conn2.tail, iface)

        # test precondition
        assert conn1.subject is conn2.subject

        case.disconnect(conn1, conn1.head)

        assert conn1.subject is None
        assert conn2.subject is None

        assert len(case.kindof(UML.Connector)) == 0
        assert len(case.kindof(UML.ConnectorEnd)) == 0
        assert len(case.kindof(UML.Port)) == 0
