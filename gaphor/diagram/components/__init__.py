from gaphor.diagram.components.artifact import ArtifactItem
from gaphor.diagram.components.component import ComponentItem
from gaphor.diagram.components.connector import ConnectorItem
from gaphor.diagram.components.node import NodeItem
from gaphor.diagram.components.subsystem import SubsystemItem


def _load():
    from gaphor.diagram.components import (
        componentsgrouping,
        connectorconnect,
        componentspropertypage,
    )


_load()
