"""
Test connector item.
"""

from gaphor import UML
from gaphor.tests.testcase import TestCase
from gaphor.UML.components.connector import ConnectorItem


class ConnectorItemTestCase(TestCase):
    """
    Connector item basic tests.
    """

    def test_create(self):
        """Test creation of connector item
        """
        conn = self.create(ConnectorItem, UML.Connector)
        assert conn.subject is not None

    def test_persistence(self):
        """Test connector item saving/loading
        """
        conn = self.create(ConnectorItem, UML.Connector)

        end = self.element_factory.create(UML.ConnectorEnd)
        conn.end = end

        data = self.save()
        assert end.id in data

        self.load(data)

        assert self.diagram.canvas.select(ConnectorItem)
        assert self.kindof(UML.ConnectorEnd)
