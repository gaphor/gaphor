from gaphor import UML
from gaphor.diagram.tests.fixtures import clear_model, connect, copy_clear_and_paste
from gaphor.UML.classes import InterfaceItem
from gaphor.UML.components import ComponentItem, ConnectorItem


def test_connector(diagram, element_factory):
    comp = element_factory.create(UML.Component)
    iface = element_factory.create(UML.Interface)

    comp_item = diagram.create(ComponentItem, subject=comp)
    iface_item = diagram.create(InterfaceItem, subject=iface)
    conn_item = diagram.create(ConnectorItem)

    connect(conn_item, conn_item.handles()[0], comp_item)
    connect(conn_item, conn_item.handles()[1], iface_item)

    copy_clear_and_paste({comp_item, iface_item, conn_item}, diagram, element_factory)

    new_conn = element_factory.lselect(lambda e: isinstance(e, UML.Connector))[0]
    new_comp = element_factory.lselect(lambda e: isinstance(e, UML.Component))[0]
    new_iface = element_factory.lselect(lambda e: isinstance(e, UML.Interface))[0]

    assert isinstance(new_conn.presentation[0], ConnectorItem)
    assert new_conn.kind == "assembly"
    assert len(new_conn.end) == 1
    assert new_conn.end[0].role is new_iface
    assert new_conn.end[0].partWithPort in new_comp.ownedPort
