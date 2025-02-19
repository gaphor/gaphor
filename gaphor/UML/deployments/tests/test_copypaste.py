from gaphor import UML
from gaphor.diagram.copypaste import copy_full, paste_full
from gaphor.diagram.tests.fixtures import connect, copy_clear_and_paste_link
from gaphor.UML.classes import ComponentItem, InterfaceItem
from gaphor.UML.deployments import ConnectorItem


def test_connector(diagram, element_factory):
    comp = element_factory.create(UML.Component)
    iface = element_factory.create(UML.Interface)

    comp_item = diagram.create(ComponentItem, subject=comp)
    iface_item = diagram.create(InterfaceItem, subject=iface)
    conn_item = diagram.create(ConnectorItem)

    connect(conn_item, conn_item.handles()[0], comp_item)
    connect(conn_item, conn_item.handles()[1], iface_item)

    copy_clear_and_paste_link(
        {comp_item, iface_item, conn_item}, diagram, element_factory
    )

    new_conn = element_factory.lselect(UML.Connector)[0]
    new_comp = element_factory.lselect(UML.Component)[0]
    new_iface = element_factory.lselect(UML.Interface)[0]

    assert isinstance(new_conn.presentation[0], ConnectorItem)
    assert new_conn.kind == "assembly"
    assert len(new_conn.end) == 1
    assert new_conn.end[0].role is new_iface
    assert new_conn.end[0].partWithPort in new_comp.ownedPort


def test_connector_end(diagram, element_factory):
    connector_end = element_factory.create(UML.ConnectorEnd)
    connector_end.lowerValue = element_factory.create(UML.LiteralInteger)
    connector_end.lowerValue.value = 1
    connector_end.upperValue = element_factory.create(UML.LiteralInteger)
    connector_end.upperValue.value = 2

    buffer = copy_full({connector_end})
    paste_full(buffer, diagram)

    new_connector_end = next(
        ce for ce in element_factory.select(UML.ConnectorEnd) if ce is not connector_end
    )

    assert new_connector_end.lowerValue
    assert new_connector_end.upperValue
    assert new_connector_end.lowerValue.value == 1
    assert new_connector_end.upperValue.value == 2

    assert new_connector_end.lowerValue is not connector_end.lowerValue
    assert new_connector_end.upperValue is not connector_end.upperValue
