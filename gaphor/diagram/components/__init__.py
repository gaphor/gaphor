from .artifact import ArtifactItem
from .component import ComponentItem
from .connector import ConnectorItem
from .node import NodeItem
from .subsystem import SubsystemItem


def _load():
    from . import componentsgrouping, connectorconnect, componentspropertypage


_load()
