"""
Test connector item connectors.
"""

from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram.components import ComponentItem
from gaphor.diagram.components import ConnectorItem
from gaphor.diagram.classes.interface import InterfaceItem
from gaphor.diagram.classes.dependency import DependencyItem
from gaphor.diagram.classes.implementation import ImplementationItem
from gaphor.diagram.components.connectorconnect import ConnectorConnectBase


class ComponentConnectTestCase(TestCase):
    """
    Test connection of connector item to a component.
    """

    def test_glue(self):
        """Test gluing connector to component."""

        component = self.create(ComponentItem, UML.Component)
        line = self.create(ConnectorItem)

        glued = self.allow(line, line.head, component)
        assert glued

    def test_connection(self):
        """Test connecting connector to a component
        """
        component = self.create(ComponentItem, UML.Component)
        line = self.create(ConnectorItem)

        self.connect(line, line.head, component)
        assert line.subject is None
        # self.assertTrue(line.end is None)

    def test_glue_both(self):
        """Test gluing connector to component when one is connected."""

        c1 = self.create(ComponentItem, UML.Component)
        c2 = self.create(ComponentItem, UML.Component)
        line = self.create(ConnectorItem)

        self.connect(line, line.head, c1)
        glued = self.allow(line, line.tail, c2)
        assert not glued


class InterfaceConnectTestCase(TestCase):
    """
    Test connection with interface acting as assembly connector.
    """

    def test_non_folded_glue(self):
        """Test non-folded interface gluing."""

        iface = self.create(InterfaceItem, UML.Component)
        line = self.create(ConnectorItem)

        glued = self.allow(line, line.head, iface)
        assert not glued

    def test_folded_glue(self):
        """Test folded interface gluing."""

        iface = self.create(InterfaceItem, UML.Component)
        line = self.create(ConnectorItem)

        iface.folded = iface.FOLDED_REQUIRED
        glued = self.allow(line, line.head, iface)
        assert glued

    def test_glue_when_dependency_connected(self):
        """Test interface gluing, when dependency connected."""

        iface = self.create(InterfaceItem, UML.Component)
        dep = self.create(DependencyItem)
        line = self.create(ConnectorItem)

        self.connect(dep, dep.head, iface)

        iface.folded = iface.FOLDED_REQUIRED
        glued = self.allow(line, line.head, iface)
        assert not glued

    def test_glue_when_implementation_connected(self):
        """Test interface gluing, when implementation connected."""

        iface = self.create(InterfaceItem, UML.Component)
        impl = self.create(ImplementationItem)
        line = self.create(ConnectorItem)

        self.connect(impl, impl.head, iface)

        iface.folded = iface.FOLDED_REQUIRED
        glued = self.allow(line, line.head, iface)
        assert not glued

    def test_glue_when_connector_connected(self):
        """Test interface gluing, when connector connected."""

        iface = self.create(InterfaceItem, UML.Component)
        iface.folded = iface.FOLDED_REQUIRED

        line1 = self.create(ConnectorItem)
        line2 = self.create(ConnectorItem)

        self.connect(line1, line1.head, iface)
        assert iface.FOLDED_ASSEMBLY == iface.folded

        glued = self.allow(line2, line2.head, iface)
        assert glued

    def test_simple_connection(self):
        """Test simple connection to an interface
        """
        iface = self.create(InterfaceItem, UML.Component)
        line = self.create(ConnectorItem)

        iface.folded = iface.FOLDED_PROVIDED
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        # test preconditions
        assert not pport.provided and not pport.required
        assert not rport.provided and not rport.required

        self.connect(line, line.head, iface, pport)
        # interface goes into assembly mode
        self.assertEqual(iface.FOLDED_ASSEMBLY, iface.folded)
        assert not iface._name.is_visible()

        # no UML metamodel yet
        self.assertTrue(line.subject is None)
        # self.assertTrue(line.end is None)

        # check port status
        self.assertTrue(pport.provided and not pport.required and pport.connectable)
        assert rport.required and not rport.provided and rport.connectable
        p1 = iface.ports()[1]
        p2 = iface.ports()[3]
        assert not p1.required and not p1.provided and not p1.connectable
        assert not p2.required and not p2.provided and not p2.connectable

    def test_connection_angle_change(self):
        """Test angle after connection to an interface
        """
        iface = self.create(InterfaceItem, UML.Component)
        line = self.create(ConnectorItem)

        iface.folded = iface.FOLDED_PROVIDED
        pport = iface.ports()[1]
        rport = iface.ports()[3]

        # test preconditions
        assert not pport.provided and not pport.required
        assert not rport.provided and not rport.required
        assert iface._angle == 0.0

        self.connect(line, line.head, iface, pport)
        assert rport.angle == iface._angle

    def test_connection_of_two_connectors_one_side(self):
        """Test connection of two connectors to required port of an interface
        """
        iface = self.create(InterfaceItem, UML.Component)
        c1 = self.create(ConnectorItem)
        c2 = self.create(ConnectorItem)

        iface.folded = iface.FOLDED_PROVIDED
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        # connect to the same interface
        self.connect(c1, c1.head, iface, pport)
        self.connect(c2, c2.head, iface, pport)

        # no UML metamodel yet
        self.assertTrue(c1.subject is None)
        # self.assertTrue(c1.end is None)
        self.assertTrue(c2.subject is None)
        # self.assertTrue(c2.end is None)

        # check port status
        self.assertTrue(pport.provided and not pport.required)
        assert rport.required and not rport.provided
        p1 = iface.ports()[1]
        p2 = iface.ports()[3]
        assert not p1.required and not p1.provided
        assert not p2.required and not p2.provided

    def test_connection_of_two_connectors_two_sides(self):
        """Test connection of two connectors to required and provided ports of an interface
        """
        iface = self.create(InterfaceItem, UML.Component)
        c1 = self.create(ConnectorItem)
        c2 = self.create(ConnectorItem)

        iface.folded = iface.FOLDED_PROVIDED
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        self.connect(c1, c1.head, iface, pport)
        self.connect(c2, c2.head, iface, rport)

        # no UML metamodel yet
        self.assertTrue(c1.subject is None)
        # self.assertTrue(c1.end is None)
        self.assertTrue(c2.subject is None)
        # self.assertTrue(c2.end is None)

        # check port status
        self.assertTrue(pport.provided and not pport.required)
        assert rport.required and not rport.provided
        p1 = iface.ports()[1]
        p2 = iface.ports()[3]
        assert not p1.required and not p1.provided
        assert not p2.required and not p2.provided

    def test_simple_disconnection(self):
        """Test disconnection of simple connection to an interface
        """
        iface = self.create(InterfaceItem, UML.Component)
        line = self.create(ConnectorItem)

        iface.folded = iface.FOLDED_PROVIDED
        pport = iface.ports()[1]

        self.connect(line, line.head, iface, pport)

        # test preconditions
        assert pport.provided and not pport.required and pport.connectable

        self.disconnect(line, line.head)
        assert iface.FOLDED_PROVIDED == iface.folded
        assert iface._angle == 0
        assert iface._name.is_visible()

        assert not any(p.provided for p in iface.ports())
        assert not any(p.required for p in iface.ports())
        assert all(p.connectable for p in iface.ports())


class AssemblyConnectorTestCase(TestCase):
    """
    Test assembly connector. It is assumed that interface and component
    connection tests defined above are working correctly.
    """

    def create_interfaces(self, *args):
        """
        Generate interfaces with names specified by arguments.

        :Paramters:
         args
            List of interface names.
        """
        for name in args:
            interface = self.element_factory.create(UML.Interface)
            interface.name = name
            yield interface

    def provide(self, component, interface):
        """
        Change component's data so it implements interfaces.
        """
        impl = self.element_factory.create(UML.Implementation)
        component.implementation = impl
        impl.contract = interface

    def require(self, component, interface):
        """
        Change component's data so it requires interface.
        """
        usage = self.element_factory.create(UML.Usage)
        component.clientDependency = usage
        usage.supplier = interface

    def test_getting_component(self):
        """Test getting component
        """
        conn1 = self.create(ConnectorItem)
        conn2 = self.create(ConnectorItem)

        c1 = self.create(ComponentItem, UML.Component)
        c2 = self.create(ComponentItem, UML.Component)

        # connect component
        self.connect(conn1, conn1.tail, c1)
        self.connect(conn2, conn2.head, c2)

        assert c1 is ConnectorConnectBase.get_component(conn1)
        assert c2 is ConnectorConnectBase.get_component(conn2)

    def test_connection(self):
        """Test basic assembly connection
        """
        conn1 = self.create(ConnectorItem)
        conn2 = self.create(ConnectorItem)

        c1 = self.create(ComponentItem, UML.Component)
        c2 = self.create(ComponentItem, UML.Component)

        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_ASSEMBLY
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        # first component provides interface
        # and the second one requires it
        self.provide(c1.subject, iface.subject)
        self.require(c2.subject, iface.subject)

        # connect component
        self.connect(conn1, conn1.head, c1)
        self.connect(conn2, conn2.head, c2)

        # make an assembly
        self.connect(conn1, conn1.tail, iface, pport)
        self.connect(conn2, conn2.tail, iface, rport)

        # test UML data model
        self.assertTrue(
            conn1.subject is conn2.subject,
            "%s is not %s" % (conn1.subject, conn2.subject),
        )
        assembly = conn1.subject
        assert isinstance(assembly, UML.Connector)
        assert "assembly" == assembly.kind

        # there should be two connector ends
        self.assertEqual(2, len(assembly.end))
        # interface is on both ends
        # end1 = conn1.end
        # end2 = conn2.end

        # self.assertTrue(end1 in assembly.end,
        #    '%s not in %s' % (end1, assembly.end))
        # self.assertTrue(end2 in assembly.end,
        #    '%s not in %s' % (end2, assembly.end))

        # self.assertEqual(end1.role, iface.subject)
        # self.assertEqual(end2.role, iface.subject)
        # ends of connector point to components
        # p1 = end1.partWithPort
        # p2 = end2.partWithPort
        # self.assertEqual(p1, c1.subject.ownedPort[0],
        #    '%s != %s' % (p1, c1.subject.ownedPort))
        # self.assertEqual(p2, c2.subject.ownedPort[0],
        #    '%s != %s' % (p2, c2.subject.ownedPort))

    def test_required_port_glue(self):
        """Test if required port gluing works."""

        conn1 = self.create(ConnectorItem)
        conn2 = self.create(ConnectorItem)

        c1 = self.create(ComponentItem, UML.Component)
        c2 = self.create(ComponentItem, UML.Component)

        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_ASSEMBLY
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        self.provide(c1.subject, iface.subject)
        self.require(c2.subject, iface.subject)

        # connect components
        self.connect(conn1, conn1.head, c1)
        self.connect(conn2, conn2.head, c2)

        self.connect(conn1, conn1.tail, iface, pport)
        glued = self.allow(conn2, conn2.tail, iface, rport)
        assert glued

    def test_wrong_port_glue(self):
        """Test if incorrect port gluing is forbidden."""

        conn1 = self.create(ConnectorItem)
        conn2 = self.create(ConnectorItem)
        conn3 = self.create(ConnectorItem)

        c1 = self.create(ComponentItem, UML.Component)
        c2 = self.create(ComponentItem, UML.Component)
        c3 = self.create(ComponentItem, UML.Component)

        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_ASSEMBLY
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        self.provide(c1.subject, iface.subject)
        self.require(c2.subject, iface.subject)
        self.require(c3.subject, iface.subject)

        # connect first two components
        self.connect(conn1, conn1.head, c1)
        self.connect(conn2, conn2.head, c2)

        self.connect(conn1, conn1.tail, iface, pport)
        self.connect(conn3, conn3.tail, iface, pport)

        # cannot allow to provided port of interface, which is required
        glued = self.allow(conn2, conn2.tail, iface, pport)
        assert not glued

        # cannot allow component, which requires an interface, when
        # connector is connected to to provided port
        glued = self.allow(conn3, conn3.head, c3)
        assert not glued

    def test_port_status(self):
        """Test if port type is set properly
        """
        conn1 = self.create(ConnectorItem)

        c1 = self.create(ComponentItem, UML.Component)

        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_ASSEMBLY
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        # component requires interface
        self.require(c1.subject, iface.subject)

        # connect component
        self.connect(conn1, conn1.head, c1)

        # first step to make an assembly
        self.connect(conn1, conn1.tail, iface, rport)

        # check port type
        self.assertTrue(pport.provided)
        assert rport.required

    def test_connection_order(self):
        """Test connection order of assembly connection
        """
        conn1 = self.create(ConnectorItem)
        conn2 = self.create(ConnectorItem)

        c1 = self.create(ComponentItem, UML.Component)
        c2 = self.create(ComponentItem, UML.Component)

        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_ASSEMBLY
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        # both components provide interface only
        self.provide(c1.subject, iface.subject)
        self.provide(c2.subject, iface.subject)

        # connect components
        self.connect(conn1, conn1.head, c1)
        self.connect(conn2, conn2.head, c2)

        # connect to provided port
        self.connect(conn1, conn1.tail, iface, pport)
        self.connect(conn2, conn2.tail, iface, pport)
        # no UML data model yet (no connection on required port)
        self.assertTrue(conn1.subject is None)
        assert conn2.subject is None
        # self.assertTrue(conn1.end is None)
        # self.assertTrue(conn2.end is None)

    def test_addtional_connections(self):
        """Test additional connections to assembly connection
        """
        conn1 = self.create(ConnectorItem)
        conn2 = self.create(ConnectorItem)
        conn3 = self.create(ConnectorItem)

        c1 = self.create(ComponentItem, UML.Component)
        c2 = self.create(ComponentItem, UML.Component)
        c3 = self.create(ComponentItem, UML.Component)

        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_ASSEMBLY
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        # provide and require interface by components
        self.provide(c1.subject, iface.subject)
        self.require(c2.subject, iface.subject)
        self.require(c3.subject, iface.subject)

        # connect components
        self.connect(conn1, conn1.head, c1)
        self.connect(conn2, conn2.head, c2)
        self.connect(conn3, conn3.head, c3)

        # create assembly
        self.connect(conn1, conn1.tail, iface, pport)
        self.connect(conn2, conn2.tail, iface, rport)

        # test precondition
        assert conn1.subject and conn2.subject

        #  additional connection
        self.connect(conn3, conn3.tail, iface, rport)

        # test UML data model
        self.assertTrue(conn3.subject is conn1.subject)
        # self.assertTrue(conn3.end is not None)

        assembly = conn1.subject

        assert 3 == len(assembly.end)

        # end3 = conn3.end

        # self.assertTrue(end3 in assembly.end,
        #    '%s not in %s' % (end3, assembly.end))

        # self.assertEqual(end3.role, iface.subject)
        # ends of connector point to components
        # p3 = end3.partWithPort
        # self.assertEqual(p3, c3.subject.ownedPort[0],
        #    '%s != %s' % (p3, c3.subject.ownedPort))

    def test_disconnection(self):
        """Test assembly connector disconnection
        """
        conn1 = self.create(ConnectorItem)
        conn2 = self.create(ConnectorItem)

        c1 = self.create(ComponentItem, UML.Component)
        c2 = self.create(ComponentItem, UML.Component)

        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_ASSEMBLY
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        # first component provides interface
        # and the second one requires it
        self.provide(c1.subject, iface.subject)
        self.require(c2.subject, iface.subject)

        # connect component
        self.connect(conn1, conn1.head, c1)
        self.connect(conn2, conn2.head, c2)

        # make an assembly
        self.connect(conn1, conn1.tail, iface, pport)
        self.connect(conn2, conn2.tail, iface, rport)

        # test precondition
        assert conn1.subject is conn2.subject

        self.disconnect(conn1, conn1.head)

        assert conn1.subject is None
        assert conn2.subject is None

        assert 0 == len(self.kindof(UML.Connector))
        assert 0 == len(self.kindof(UML.ConnectorEnd))
        assert 0 == len(self.kindof(UML.Port))

    def test_disconnection_order(self):
        """Test assembly connector disconnection order
        """
        conn1 = self.create(ConnectorItem)
        conn2 = self.create(ConnectorItem)
        conn3 = self.create(ConnectorItem)

        c1 = self.create(ComponentItem, UML.Component)
        c2 = self.create(ComponentItem, UML.Component)
        c3 = self.create(ComponentItem, UML.Component)

        iface = self.create(InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_ASSEMBLY
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        # provide and require interface
        self.provide(c1.subject, iface.subject)
        self.require(c2.subject, iface.subject)
        self.require(c3.subject, iface.subject)

        # connect components
        self.connect(conn1, conn1.head, c1)
        self.connect(conn2, conn2.head, c2)
        self.connect(conn3, conn3.head, c3)

        # make assembly
        self.connect(conn1, conn1.tail, iface, pport)
        self.connect(conn2, conn2.tail, iface, rport)
        self.connect(conn3, conn3.tail, iface, rport)

        # test precondition
        assert conn1.subject is conn2.subject is conn3.subject

        # disconnect from provided port
        # assembly should be destroyed
        self.disconnect(conn1, conn1.head)

        assert conn1.subject is None
        assert conn2.subject is None
        assert conn3.subject is None

        assert 0 == len(self.kindof(UML.Connector))
        assert 0 == len(self.kindof(UML.ConnectorEnd))
        assert 0 == len(self.kindof(UML.Port))
