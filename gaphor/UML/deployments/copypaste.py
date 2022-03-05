from gaphor.diagram.copypaste import copy, copy_element
from gaphor.UML import Connector, ConnectorEnd
from gaphor.UML.copypaste import copy_named_element


@copy.register
def copy_connector(element: Connector):
    yield element.id, copy_named_element(element)
    for end in element.end:
        yield from copy(end)


@copy.register
def copy_connector_end(element: ConnectorEnd):
    yield element.id, copy_element(element)
    if element.partWithPort:
        yield from copy(element.partWithPort)
