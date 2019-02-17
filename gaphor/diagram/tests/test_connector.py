"""
Test connector item.
"""

from gaphor import UML
from gaphor.diagram.connector import ConnectorItem
from gaphor.tests.testcase import TestCase


class ConnectorItemTestCase(TestCase):
    """
    Connector item basic tests.
    """

    def test_create(self):
        """Test creation of connector item
        """
        conn = self.create(ConnectorItem, UML.Connector)
        self.assertFalse(conn.subject is None)
        # self.assertTrue(conn.end is None)

    def test_name(self):
        """Test connected interface name
        """
        conn = self.create(ConnectorItem, UML.Connector)
        end = self.element_factory.create(UML.ConnectorEnd)
        iface = self.element_factory.create(UML.Interface)
        end.role = iface
        conn.subject.end = end
        # conn.end = end
        # self.assertTrue(conn._end is end)

        self.assertEqual("", conn._interface.text)

        iface.name = "RedSea"
        self.assertEqual("RedSea", conn._interface.text)

    def test_setting_end(self):
        """Test creation of connector item
        """
        conn = self.create(ConnectorItem, UML.Connector)
        end = self.element_factory.create(UML.ConnectorEnd)
        iface = self.element_factory.create(UML.Interface)
        end.role = iface
        iface.name = "RedSea"
        conn.subject.end = end
        # conn.end = end
        # self.assertTrue(conn._end is end)
        self.assertEqual("RedSea", conn._interface.text)

        del conn.subject.end[end]
        conn.end = None
        self.assertEqual("", conn._interface.text)

    def test_persistence(self):
        """Test connector item saving/loading
        """
        conn = self.create(ConnectorItem, UML.Connector)

        end = self.element_factory.create(UML.ConnectorEnd)
        # conn.end = end

        data = self.save()
        self.assertTrue(end.id in data)

        self.load(data)

        connectors = self.diagram.canvas.select(lambda e: isinstance(e, ConnectorItem))
        ends = self.kindof(UML.ConnectorEnd)
        # self.assertTrue(connectors[0].end is not None)
        # self.assertTrue(connectors[0].end is ends[0])
