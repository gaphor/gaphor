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


    def setUp(self):
        """
        Create two components and a connector item line. Adapter for
        connecting components with connector is created as well.
        """
        super(AssemblyConnectorTestCase, self).setUp()

        self.c1 = self.create(items.ComponentItem, UML.Component)
        self.c2 = self.create(items.ComponentItem, UML.Component)
        self.line = self.create(items.ConnectorItem)
        query = (self.c1, self.line)
        self.adapter = component.queryMultiAdapter(query, IConnect)


    def test_component_intersection(self):
        """Test component intersection of provided and required interfaces"""

        i1, i2 = self._create_interfaces('A', 'B')

        # no components, no interfaces
        interfaces = self.adapter._get_interfaces(None, None)
        self.assertEquals([], interfaces)

        # no provided/required interfaces
        interfaces = self.adapter._get_interfaces(self.c1, self.c2)
        self.assertEquals([], interfaces)

        # c1 provides i1
        self._provide(self.c1.subject, i1)
        interfaces = self.adapter._get_interfaces(self.c1, self.c2)
        self.assertEquals([], interfaces)

        # c1 provides i1 and c2 requires i1
        self._require(self.c2.subject, i1)
        interfaces = self.adapter._get_interfaces(self.c1, self.c2)
        self.assertEquals([i1], interfaces)

        # c1 provides i1 and i2, c2 requires i1 only 
        self._provide(self.c1.subject, i2)
        interfaces = self.adapter._get_interfaces(self.c1, self.c2)
        self.assertEquals([i1], interfaces)

        # both components require and provide interfaces i1 and i2
        self._require(self.c2.subject, i2)
        interfaces = self.adapter._get_interfaces(self.c1, self.c2)
        self.assertEquals([i1, i2], interfaces)


    def test_component_glue(self):
        """Test glueing components with assembly connector.
        """
        glued = self.adapter.glue(self.line.head)
        self.assertFalse(glued) # no interfaces, no glue

        glued = self.adapter.glue(self.line.tail)
        self.assertFalse(glued) # no interfaces, no glue



# vim:sw=4:et:ai
