"""
Test connector item connectors.
"""

from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram import items


class ComponentConnectTestCase(TestCase):
    """
    Test connection of connector item to a component.
    """
    def test_glue(self):
        """Test glueing connector to component
        """
        component = self.create(items.ComponentItem, UML.Component)
        line = self.create(items.ConnectorItem)

        glued = self.glue(line, line.head, component)
        self.assertTrue(glued)


    def test_connection(self):
        """Test connecting connector to a component
        """
        component = self.create(items.ComponentItem, UML.Component)
        line = self.create(items.ConnectorItem)

        self.connect(line, line.head, component)
        self.assertTrue(line.subject is None)
        self.assertTrue(line.end is None)


    def test_glue_both(self):
        """Test glueing connector to component when one is connected
        """
        c1 = self.create(items.ComponentItem, UML.Component)
        c2 = self.create(items.ComponentItem, UML.Component)
        line = self.create(items.ConnectorItem)

        self.connect(line, line.head, c1)
        glued = self.glue(line, line.tail, c2)
        self.assertFalse(glued)



class InterfaceConnectTestCase(TestCase):
    """
    Test connection with interface acting as assembly connector.
    """
    def test_non_folded_glue(self):
        """Test non-folded interface glueing
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        line = self.create(items.ConnectorItem)

        glued = self.glue(line, line.head, iface)
        self.assertFalse(glued)


    def test_folded_glue(self):
        """Test folded interface glueing
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        line = self.create(items.ConnectorItem)

        iface.folded = iface.FOLDED_REQUIRED
        glued = self.glue(line, line.head, iface)
        self.assertTrue(glued)


    def test_glue_when_dependency_connected(self):
        """Test interface glueing, when dependency connected
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        dep = self.create(items.DependencyItem)
        line = self.create(items.ConnectorItem)

        self.connect(dep, dep.head, iface)

        iface.folded = iface.FOLDED_REQUIRED
        glued = self.glue(line, line.head, iface)
        self.assertFalse(glued)


    def test_glue_when_implementation_connected(self):
        """Test interface glueing, when implementation connected
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        impl = self.create(items.ImplementationItem)
        line = self.create(items.ConnectorItem)

        self.connect(impl, impl.head, iface)

        iface.folded = iface.FOLDED_REQUIRED
        glued = self.glue(line, line.head, iface)
        self.assertFalse(glued)


    def test_glue_when_connector_connected(self):
        """Test interface glueing, when connector connected
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        iface.folded = iface.FOLDED_REQUIRED

        line1 = self.create(items.ConnectorItem)
        line2 = self.create(items.ConnectorItem)

        self.connect(line1, line1.head, iface)
        self.assertEquals(iface.FOLDED_ASSEMBLY, iface.folded)

        glued = self.glue(line2, line2.head, iface)
        self.assertTrue(glued)


    def test_simple_connection(self):
        """Test simple connection to an interface
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        line = self.create(items.ConnectorItem)

        iface.folded = iface.FOLDED_PROVIDED
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        # test preconditions
        assert not pport.provided and not pport.required
        assert not rport.provided and not rport.required

        self.connect(line, line.head, iface, pport)
        # interface goes into assembly mode
        self.assertEquals(iface.FOLDED_ASSEMBLY, iface.folded)
        self.assertFalse(iface._name.is_visible())

        # no UML metamodel yet
        self.assertTrue(line.subject is None)
        self.assertTrue(line.end is None)

        # check port status
        self.assertTrue(pport.provided and not pport.required and pport.connectable)
        self.assertTrue(rport.required and not rport.provided and rport.connectable)
        p1 = iface.ports()[1]
        p2 = iface.ports()[3]
        self.assertTrue(not p1.required and not p1.provided and not p1.connectable)
        self.assertTrue(not p2.required and not p2.provided and not p2.connectable)


    def test_connection_angle_change(self):
        """Test angle after connection to an interface
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        line = self.create(items.ConnectorItem)

        iface.folded = iface.FOLDED_PROVIDED
        pport = iface.ports()[1]
        rport = iface.ports()[3]

        # test preconditions
        assert not pport.provided and not pport.required
        assert not rport.provided and not rport.required
        assert iface._angle == 0.0

        self.connect(line, line.head, iface, pport)
        self.assertEquals(rport.angle, iface._angle)


    def test_connection_of_two_connectors_one_side(self):
        """Test connection of two connectors to required port of an interface
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        c1 = self.create(items.ConnectorItem)
        c2 = self.create(items.ConnectorItem)

        iface.folded = iface.FOLDED_PROVIDED
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        # connect to the same interface
        self.connect(c1, c1.head, iface, pport)
        self.connect(c2, c2.head, iface, pport)

        # no UML metamodel yet
        self.assertTrue(c1.subject is None)
        self.assertTrue(c1.end is None)
        self.assertTrue(c2.subject is None)
        self.assertTrue(c2.end is None)

        # check port status
        self.assertTrue(pport.provided and not pport.required)
        self.assertTrue(rport.required and not rport.provided)
        p1 = iface.ports()[1]
        p2 = iface.ports()[3]
        self.assertTrue(not p1.required and not p1.provided)
        self.assertTrue(not p2.required and not p2.provided)


    def test_connection_of_two_connectors_two_sides(self):
        """Test connection of two connectors to required and provided ports of an interface
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        c1 = self.create(items.ConnectorItem)
        c2 = self.create(items.ConnectorItem)

        iface.folded = iface.FOLDED_PROVIDED
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        self.connect(c1, c1.head, iface, pport)
        self.connect(c2, c2.head, iface, rport)

        # no UML metamodel yet
        self.assertTrue(c1.subject is None)
        self.assertTrue(c1.end is None)
        self.assertTrue(c2.subject is None)
        self.assertTrue(c2.end is None)

        # check port status
        self.assertTrue(pport.provided and not pport.required)
        self.assertTrue(rport.required and not rport.provided)
        p1 = iface.ports()[1]
        p2 = iface.ports()[3]
        self.assertTrue(not p1.required and not p1.provided)
        self.assertTrue(not p2.required and not p2.provided)


    def test_simple_disconnection(self):
        """Test disconnection of simple connection to an interface
        """
        iface = self.create(items.InterfaceItem, UML.Component)
        line = self.create(items.ConnectorItem)

        iface.folded = iface.FOLDED_PROVIDED
        pport = iface.ports()[1]

        self.connect(line, line.head, iface, pport)

        # test preconditions
        assert pport.provided and not pport.required and pport.connectable

        self.disconnect(line, line.head)
        self.assertEquals(iface.FOLDED_PROVIDED, iface.folded)
        self.assertEquals(iface._angle, 0)
        self.assertTrue(iface._name.is_visible())

        self.assertFalse(any(p.provided for p in iface.ports()))
        self.assertFalse(any(p.required for p in iface.ports()))
        self.assertTrue(all(p.connectable for p in iface.ports()))



class AssemblyConnectorTestCase(TestCase):
    """
    Test assembly connector. It is assumed that interface and component
    connection tests defined above are working correctly.
    """
    def create_interfaces(self, *args):
        """
        Generate interfaces with names sepecified by arguments.

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


    def test_connection(self):
        """Test basic assembly connection
        """
        conn1 = self.create(items.ConnectorItem)
        conn2 = self.create(items.ConnectorItem)

        c1 = self.create(items.ComponentItem, UML.Component)
        c2 = self.create(items.ComponentItem, UML.Component)

        iface = self.create(items.InterfaceItem, UML.Interface)
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
        self.assertTrue(conn1.subject is conn2.subject,
            '%s is not %s' % (conn1.subject, conn2.subject))
        assembly = conn1.subject
        self.assertTrue(isinstance(assembly, UML.Connector))
        self.assertEquals('assembly', assembly.kind)

        # there should be two connector ends
        self.assertEquals(2, len(assembly.end))
        # interface is on both ends
        end1 = conn1.end
        end2 = conn2.end

        self.assertTrue(end1 in assembly.end,
            '%s not in %s' % (end1, assembly.end))
        self.assertTrue(end2 in assembly.end,
            '%s not in %s' % (end2, assembly.end))

        self.assertEquals(end1.role, iface.subject)
        self.assertEquals(end2.role, iface.subject)
        # ends of connector point to components 
        p1 = end1.partWithPort
        p2 = end2.partWithPort
        self.assertEquals(p1, c1.subject.ownedPort,
            '%s != %s' % (p1, c1.subject.ownedPort))
        self.assertEquals(p2, c2.subject.ownedPort,
            '%s != %s' % (p2, c2.subject.ownedPort))


    def test_required_port_glue(self):
        """Test if required port glueing works
        """
        conn1 = self.create(items.ConnectorItem)
        conn2 = self.create(items.ConnectorItem)

        c1 = self.create(items.ComponentItem, UML.Component)
        c2 = self.create(items.ComponentItem, UML.Component)

        iface = self.create(items.InterfaceItem, UML.Interface)
        iface.folded = iface.FOLDED_ASSEMBLY
        pport = iface.ports()[0]
        rport = iface.ports()[2]

        self.provide(c1.subject, iface.subject)
        self.require(c2.subject, iface.subject)

        # connect components
        self.connect(conn1, conn1.head, c1)
        self.connect(conn2, conn2.head, c2)

        self.connect(conn1, conn1.tail, iface, pport)
        glued = self.glue(conn2, conn2.tail, iface, rport)
        self.assertTrue(glued)


    def test_wrong_port_glue(self):
        """Test if incorrect port glueing is forbidden
        """
        conn1 = self.create(items.ConnectorItem)
        conn2 = self.create(items.ConnectorItem)
        conn3 = self.create(items.ConnectorItem)

        c1 = self.create(items.ComponentItem, UML.Component)
        c2 = self.create(items.ComponentItem, UML.Component)
        c3 = self.create(items.ComponentItem, UML.Component)

        iface = self.create(items.InterfaceItem, UML.Interface)
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

        # cannot glue to provided port of interface, which is required
        glued = self.glue(conn2, conn2.tail, iface, pport)
        self.assertFalse(glued)

        # cannot glue component, which requires an interface, when
        # connector is connected to to provided port
        glued = self.glue(conn3, conn3.head, c3)
        self.assertFalse(glued)


    def test_port_status(self):
        """Test if port type is set properly
        """
        conn1 = self.create(items.ConnectorItem)

        c1 = self.create(items.ComponentItem, UML.Component)

        iface = self.create(items.InterfaceItem, UML.Interface)
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
        self.assertTrue(rport.required)


    def test_connection_order(self):
        """Test connection order of assembly connection
        """
        conn1 = self.create(items.ConnectorItem)
        conn2 = self.create(items.ConnectorItem)

        c1 = self.create(items.ComponentItem, UML.Component)
        c2 = self.create(items.ComponentItem, UML.Component)

        iface = self.create(items.InterfaceItem, UML.Interface)
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
        # no UML data model yet (no connection on provided port)
        self.assertTrue(conn1.subject is None)
        self.assertTrue(conn2.subject is None)
        self.assertTrue(conn1.end is None)
        self.assertTrue(conn2.end is None)


    def test_addtional_connections(self):
        """Test additional connections to assembly connection
        """
        conn1 = self.create(items.ConnectorItem)
        conn2 = self.create(items.ConnectorItem)
        conn3 = self.create(items.ConnectorItem)

        c1 = self.create(items.ComponentItem, UML.Component)
        c2 = self.create(items.ComponentItem, UML.Component)
        c3 = self.create(items.ComponentItem, UML.Component)

        iface = self.create(items.InterfaceItem, UML.Interface)
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
        self.assertTrue(conn3.end is not None)

        assembly = conn1.subject

        self.assertEquals(3, len(assembly.end))

        end3 = conn3.end

        self.assertTrue(end3 in assembly.end,
            '%s not in %s' % (end3, assembly.end))

        self.assertEquals(end3.role, iface.subject)
        # ends of connector point to components 
        p3 = end3.partWithPort
        self.assertEquals(p3, c3.subject.ownedPort,
            '%s != %s' % (p3, c3.subject.ownedPort))


    def test_disconnection(self):
        """Test assembly connector disconnection
        """
        conn1 = self.create(items.ConnectorItem)
        conn2 = self.create(items.ConnectorItem)

        c1 = self.create(items.ComponentItem, UML.Component)
        c2 = self.create(items.ComponentItem, UML.Component)

        iface = self.create(items.InterfaceItem, UML.Interface)
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

        self.assertTrue(conn1.subject is None)
        self.assertTrue(conn2.subject is None)
        
        self.assertEquals(0, len(self.kindof(UML.Connector)))
        self.assertEquals(0, len(self.kindof(UML.ConnectorEnd)))
        self.assertEquals(0, len(self.kindof(UML.Port)))


    def test_disconnection_order(self):
        """Test assembly connector disconnection order
        """
        conn1 = self.create(items.ConnectorItem)
        conn2 = self.create(items.ConnectorItem)
        conn3 = self.create(items.ConnectorItem)

        c1 = self.create(items.ComponentItem, UML.Component)
        c2 = self.create(items.ComponentItem, UML.Component)
        c3 = self.create(items.ComponentItem, UML.Component)

        iface = self.create(items.InterfaceItem, UML.Interface)
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

        self.assertTrue(conn1.subject is None)
        self.assertTrue(conn2.subject is None)
        self.assertTrue(conn3.subject is None)
        
        self.assertEquals(0, len(self.kindof(UML.Connector)))
        self.assertEquals(0, len(self.kindof(UML.ConnectorEnd)))
        self.assertEquals(0, len(self.kindof(UML.Port)))



# vim:sw=4:et:ai
