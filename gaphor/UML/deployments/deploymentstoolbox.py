"""The definition for the components section of the toolbox."""

from gaphas.item import SE

from gaphor import UML
from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection, new_element_item_factory
from gaphor.UML.toolboxconfig import namespace_config

deployments: ToolSection = ToolSection(
    gettext("Deployments"),
    (
        ToolDef(
            "toolbox-artifact",
            gettext("Artifact"),
            "gaphor-artifact-symbolic",
            "h",
            new_element_item_factory(
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
            new_element_item_factory(
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
            new_element_item_factory(
                UML.Device,
                config_func=namespace_config,
            ),
            handle_index=SE,
        ),
    ),
)
