import itertools
from typing import List, NamedTuple

from gaphor.diagram.copypaste import (
    ElementCopy,
    copy,
    copy_element,
    paste,
    paste_element,
)
from gaphor.UML import Connector


class ConnectorCopy(NamedTuple):
    element_copy: ElementCopy
    ends: List[ElementCopy]
    ports: List[ElementCopy]


@copy.register
def copy_connector(element: Connector):
    return ConnectorCopy(
        element_copy=copy_element(element),
        ends=[copy_element(end) for end in element.end],
        ports=[copy_element(port) for port in element.end[:].partWithPort],
    )


@paste.register
def paste_connector(copy_data: ConnectorCopy, diagram, lookup):
    for data in itertools.chain(copy_data.ports, copy_data.ends):
        paste_element(data, diagram, lookup)
    return paste_element(copy_data.element_copy, diagram, lookup)
