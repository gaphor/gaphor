"""
Test connector item connectors.
"""

from gaphor.tests import TestCase
from zope import component
from gaphor import UML
from gaphor.diagram import items
from gaphor.diagram.interfaces import IConnect

class TestCaseBase(TestCase):
    def _create_interfaces(self, *args):
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


    def _provide(self, component, interface):
        """
        Change component's data so it implements interfaces.
        """
        impl = self.element_factory.create(UML.Implementation)
        component.implementation = impl
        impl.contract = interface


    def _require(self, component, interface):
        """
        Change component's data so it requires interface.
        """
        usage = self.element_factory.create(UML.Usage)
        component.clientDependency = usage
        usage.supplier = interface


    def setUp(self):
        """
        Create two components and a connector item line. Adapter for
        connecting components with connector is created as well.
        """
        super(TestCaseBase, self).setUp()

        self.c1 = self.create(items.ComponentItem, UML.Component)
        self.c2 = self.create(items.ComponentItem, UML.Component)
        self.line = self.create(items.ConnectorItem)

        # no subject for assembly by default
        self.assembly = self.create(items.AssemblyConnectorItem)



class AssemblyConnectorConnectTestCase(TestCaseBase):
    """
    Test components connection with assembly connector.
    """
    def test_ac_glue(self):
        """Test assembly connector glueing
        """
        assembly = self.assembly
        pport = assembly._provided_port
        rport = assembly._required_port
        head, tail = self.line.head, self.line.tail

        glued = self.glue(self.line, head, assembly, rport)
        self.assertTrue(glued)

        glued = self.glue(self.line, head, assembly, pport)
        self.assertFalse(glued)

        glued = self.glue(self.line, tail, assembly, rport)
        self.assertFalse(glued)

        glued = self.glue(self.line, tail, assembly, pport)
        self.assertTrue(glued)


    def test_component_glue(self):
        """Test component glueing
        """
        glued = self.glue(self.line, self.line.head, self.c1)
        self.assertTrue(glued)

        glued = self.glue(self.line, self.line.tail, self.c1)
        self.assertTrue(glued)


    def test_ac_connection(self):
        """Test assembly connector connection
        """
        assembly = self.assembly
        head = self.line.head
        self.connect(self.line, head, assembly, assembly._required_port)

        self.assertTrue(self.line.subject is None)
        self.assertTrue(self.assembly.subject is None)


    def test_component_connection(self):
        """Test component connection
        """
        self.connect(self.line, self.line.head, self.c1)
        self.assertTrue(self.line.subject is None)
        self.assertTrue(self.assembly.subject is None)


    def test_one_component_connection(self):
        """Test assembly connector connection with one component
        """
        assembly = self.assembly
        head, tail = self.line.head, self.line.tail

        self.connect(self.line, head, assembly, assembly._required_port)
        self.connect(self.line, tail, self.c1)

        # one component created, no assembly connector yet
        self.assertTrue(assembly.subject is None)
        self.assertTrue(self.line.subject is None)


    # tests below to be fixed

    def test_connector_grouping(self):
        """Test assembly connectors grouping
        """
        self.connect(self.line, self.line.head, self.c1)

        i1, = self._create_interfaces('A')
        self._provide(self.c1.subject, i1)
        self._require(self.c2.subject, i1)

        connected = self.connect(self.line, self.line.tail, self.c2)
        assert connected

        assembly = self.create(items.ConnectorItem)
        c3 = self.create(items.ComponentItem, UML.Component)
        self._provide(c3.subject, i1)
        self.connect(assembly, assembly.head, c3)

        connected = self.connect(assembly, assembly.tail, self.line, self.line._provided_port)
        self.assertTrue(connected)

        # test UML data model
        # is connector really connector?
        self.assertTrue(isinstance(assembly.subject, UML.Connector))
        connector = assembly.subject
        # there should be two connector ends
        self.assertEquals(2, len(connector.end))
        # interface i1 is on both ends
        end1 = connector.end[0]
        end2 = connector.end[1]
        self.assertEquals(i1, end1.role)
        self.assertEquals(i1, end2.role)
        # connector ends identify components 
        p1 = end1.partWithPort
        p2 = end2.partWithPort
        self.assertEquals(p1, c3.subject.ownedPort)
        self.assertEquals(p2, self.c2.subject.ownedPort)
        # it is assembly connector
        self.assertEquals('assembly', connector.kind)
        self.assertTrue(assembly.is_assembly)


    def test_groupped_connector_disconnection(self):
        """Test groupped assembly connectors disconnection
        """
        self.connect(self.line, self.line.head, self.c1)

        i1, = self._create_interfaces('A')
        self._provide(self.c1.subject, i1)
        self._require(self.c2.subject, i1)

        connected = self.connect(self.line, self.line.tail, self.c2)
        assert connected

        assembly = self.create(items.ConnectorItem)
        c3 = self.create(items.ComponentItem, UML.Component)
        self._provide(c3.subject, i1)
        self.connect(assembly, assembly.head, c3)

        connected = self.connect(assembly, assembly.tail, self.line, self.line._provided_port)
        assert connected

        self.disconnect(assembly, assembly.tail)
        
        self.assertEquals(1, len(self.kindof(UML.Connector)))
        self.assertEquals([self.line.subject], self.kindof(UML.Connector))
        self.assertEquals(2, len(self.kindof(UML.ConnectorEnd)))
        self.assertEquals(2, len(self.kindof(UML.Port)))


    def test_component_intersection(self):
        """Test component intersection of provided and required interfaces"""

        i1, i2 = self._create_interfaces('A', 'B')

        query = (self.c1, self.line)
        adapter = component.queryMultiAdapter(query, IConnect)

        # no provided/required interfaces
        interfaces = adapter._get_interfaces(self.c1, self.c2)
        self.assertEquals([], interfaces)

        # c1 provides i1
        self._provide(self.c1.subject, i1)
        interfaces = adapter._get_interfaces(self.c1, self.c2)
        self.assertEquals([], interfaces)

        # c1 provides i1 and c2 requires i1
        self._require(self.c2.subject, i1)
        interfaces = adapter._get_interfaces(self.c1, self.c2)
        self.assertEquals([i1], interfaces)

        # c1 provides i1 and i2, c2 requires i1 only 
        self._provide(self.c1.subject, i2)
        interfaces = adapter._get_interfaces(self.c1, self.c2)
        self.assertEquals([i1], interfaces)

        # both components require and provide interfaces i1 and i2
        self._require(self.c2.subject, i2)
        interfaces = adapter._get_interfaces(self.c1, self.c2)
        self.assertEquals([i1, i2], interfaces)


    def test_components_connection(self):
        """Test components connection
        """
        self.connect(self.line, self.line.head, self.c1)

        i1, = self._create_interfaces('A')
        self._provide(self.c1.subject, i1)
        self._require(self.c2.subject, i1)

        self.assertFalse(self.line.is_assembly)

        connected = self.connect(self.line, self.line.tail, self.c2)
        self.assertTrue(connected)

        # test UML data model
        # is connector really connector?
        self.assertTrue(isinstance(self.line.subject, UML.Connector))
        connector = self.line.subject
        # there should be two connector ends
        self.assertEquals(2, len(connector.end))
        # interface i1 is on both ends
        end1 = connector.end[0]
        end2 = connector.end[1]
        self.assertEquals(i1, end1.role)
        self.assertEquals(i1, end2.role)
        # connector ends identify components 
        p1 = end1.partWithPort
        p2 = end2.partWithPort
        self.assertEquals(p1, self.c1.subject.ownedPort)
        self.assertEquals(p2, self.c2.subject.ownedPort)
        # it is assembly connector
        self.assertEquals('assembly', connector.kind)
        self.assertTrue(self.line.is_assembly)


    def test_disconnection(self):
        """Test assembly connector disconnection
        """
        self.connect(self.line, self.line.head, self.c1)

        i1, = self._create_interfaces('A')
        self._provide(self.c1.subject, i1)
        self._require(self.c2.subject, i1)

        connected = self.connect(self.line, self.line.tail, self.c2)
        assert connected

        self.disconnect(self.line, self.line.head)
        
        self.assertEquals(0, len(self.kindof(UML.Connector)))
        self.assertEquals(0, len(self.kindof(UML.ConnectorEnd)))
        self.assertEquals(0, len(self.kindof(UML.Port)))


# vim:sw=4:et:ai
