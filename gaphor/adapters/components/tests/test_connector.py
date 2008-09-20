"""
Test connector item connectors.
"""

from gaphor.tests import TestCase
from zope import component
from gaphor import UML
from gaphor.diagram import items
from gaphor.diagram.interfaces import IConnect

class AssemblyConnectorTestCase(TestCase):
    """
    Test components connection with assembly connector.
    """

    services = ['element_factory', 'adapter_loader']

    def _create_interfaces(self, *args):
        """
        Generate interfaces with names sepecified by arguments.

        :Paramters:
         args
            List of interface names.
        """
        for name in args:
            interface = self.element_factory.create(UML.Interface)
            interface.name = 'B'
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


    def _glue(self, line, handle, item, port=None):
        """
        Glue line's handle to an item.
        """
        query = (item, line)
        adapter = component.queryMultiAdapter(query, IConnect)
        return adapter.glue(handle, port)


    def _connect(self, line, handle, item, port=None):
        """
        Connect line's handle to an item.
        """
        query = (item, line)
        handle.connected_to = item
        try:
            adapter = component.queryMultiAdapter(query, IConnect)
            return adapter.connect(handle, port)
        except Error, ex:
            handle.connected_to = None
            raise ex


    def _disconnect(self, line, handle):
        """
        Disconnect line's handle.
        """
        query = (handle.connected_to, line)
        adapter = component.queryMultiAdapter(query, IConnect)
        adapter.disconnect(self.line.head)


    def _kindof(self, cls):
        """
        Find UML metaclass instances using element factory.
        """
        return self.element_factory.lselect(lambda e: e.isKindOf(cls))


    def setUp(self):
        """
        Create two components and a connector item line. Adapter for
        connecting components with connector is created as well.
        """
        super(AssemblyConnectorTestCase, self).setUp()

        self.c1 = self.create(items.ComponentItem, UML.Component)
        self.c2 = self.create(items.ComponentItem, UML.Component)
        self.line = self.create(items.ConnectorItem)


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


    def test_component_one_side_glue(self):
        """Test glueing first component
        """
        glued = self._glue(self.line, self.line.head, self.c1)
        self.assertTrue(glued)


    def test_component_glue_no_interfaces(self):
        """Test glueing components with no interfaces using assembly connector
        """
        self._connect(self.line, self.line.head, self.c1)
        glued = self._glue(self.line, self.line.tail, self.c2)
        self.assertFalse(glued)


    def test_components_glue(self):
        """Test glueing components
        """
        self._connect(self.line, self.line.head, self.c1)

        i1, = self._create_interfaces('A')
        self._provide(self.c1.subject, i1)
        self._require(self.c2.subject, i1)

        glued = self._glue(self.line, self.line.tail, self.c2)
        self.assertTrue(glued)


    def test_components_glue_switched(self):
        """Test glueing components in different order
        """
        self._connect(self.line, self.line.tail, self.c2)

        i1, = self._create_interfaces('A')
        self._provide(self.c1.subject, i1)
        self._require(self.c2.subject, i1)

        glued = self._glue(self.line, self.line.head, self.c1)
        self.assertTrue(glued)


    def test_components_connection(self):
        """Test components connection
        """
        self._connect(self.line, self.line.head, self.c1)

        i1, = self._create_interfaces('A')
        self._provide(self.c1.subject, i1)
        self._require(self.c2.subject, i1)

        connected = self._connect(self.line, self.line.tail, self.c2)
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


    def test_disconnection(self):
        """Test assembly connector disconnection
        """
        self._connect(self.line, self.line.head, self.c1)

        i1, = self._create_interfaces('A')
        self._provide(self.c1.subject, i1)
        self._require(self.c2.subject, i1)

        connected = self._connect(self.line, self.line.tail, self.c2)
        assert connected

        self._disconnect(self.line, self.line.head)
        
        factory = self.element_factory
        self.assertEquals(0, len(self._kindof(UML.Connector)))
        self.assertEquals(0, len(self._kindof(UML.ConnectorEnd)))
        self.assertEquals(0, len(self._kindof(UML.Port)))



# vim:sw=4:et:ai
