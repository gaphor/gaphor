"""The definition for the components section of the toolbox."""

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection, namespace_config
from gaphor.diagram.diagramtools import PlacementTool
from gaphor.UML import diagramitems

components: ToolSection = ToolSection(
    gettext("Components"),
    (
        ToolDef(
            "toolbox-component",
            gettext("Component"),
            "gaphor-component-symbolic",
            "o",
            PlacementTool.new_item_factory(
                diagramitems.ComponentItem,
                UML.Component,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-artifact",
            gettext("Artifact"),
            "gaphor-artifact-symbolic",
            "h",
            PlacementTool.new_item_factory(
                diagramitems.ArtifactItem,
                UML.Artifact,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-node",
            gettext("Node"),
            "gaphor-node-symbolic",
            "n",
            PlacementTool.new_item_factory(
                diagramitems.NodeItem,
                UML.Node,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
        ToolDef(
            "toolbox-device",
            gettext("Device"),
            "gaphor-device-symbolic",
            "d",
            PlacementTool.new_item_factory(
                diagramitems.NodeItem,
                UML.Device,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
    ),
)
