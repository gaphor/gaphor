"""Test connector item."""

from gaphor import UML
from gaphor.UML.components.connector import ConnectorItem


class TestConnectorItem:
    """Connector item basic tests."""

    def test_create(self, case):
        """Test creation of connector item."""
        conn = case.create(ConnectorItem, UML.Connector)
        assert conn.subject is not None

    def test_persistence(self, case):
        """Test connector item saving/loading."""
        conn = case.create(ConnectorItem, UML.Connector)

        end = case.element_factory.create(UML.ConnectorEnd)
        conn.end = end

        data = case.save()
        assert end.id in data

        case.load(data)

        assert case.diagram.select(ConnectorItem)
        assert case.kindof(UML.ConnectorEnd)
