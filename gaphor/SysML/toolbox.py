"""The action definition for the SysML toolbox."""

from gaphor import UML
from gaphor.i18n import gettext, i18nize
from gaphor.diagram.diagramtoolbox import (
    DiagramType,
    DiagramTypes,
    ToolboxDefinition,
    ToolDef,
    ToolSection,
    general_tools,
    new_item_factory,
)
from gaphor.SysML import diagramitems as sysml_items
from gaphor.SysML.blocks.blockstoolbox import blocks
from gaphor.SysML.requirements.requirementstoolbox import requirements
from gaphor.UML import diagramitems as uml_items
from gaphor.UML.actions.actionstoolbox import actions
from gaphor.UML.interactions.interactionstoolbox import interactions
from gaphor.UML.states.statestoolbox import states
from gaphor.UML.toolboxconfig import named_element_config
from gaphor.UML.usecases.usecasetoolbox import use_cases

internal_blocks = ToolSection(
    gettext("Internal Blocks"),
    (
        ToolDef(
            "toolbox-connector",
            gettext("Connector"),
            "gaphor-connector-symbolic",
            "<Shift>C",
            new_item_factory(uml_items.ConnectorItem),
        ),
        ToolDef(
            "toolbox-property",
            gettext("Property"),
            "gaphor-property-symbolic",
            "o",
            new_item_factory(
                sysml_items.PropertyItem, UML.Property, config_func=named_element_config
            ),
        ),
        ToolDef(
            "toolbox-proxy-port",
            gettext("Proxy Port"),
            "gaphor-proxyport-symbolic",
            "x",
            new_item_factory(sysml_items.ProxyPortItem),
        ),
    ),
)


sysml_toolbox_actions: ToolboxDefinition = (
    general_tools,
    blocks,
    internal_blocks,
    requirements,
    actions,
    interactions,
    states,
    use_cases,
)


# Not implemented: Parameter Diagram
sysml_diagram_types: DiagramTypes = (
    DiagramType("bdd", i18nize("New Block Definition Diagram"), (blocks,)),
    DiagramType("ibd", i18nize("New Internal Block Diagram"), (internal_blocks,)),
    DiagramType("pkg", i18nize("New Package Diagram"), (blocks,)),
    DiagramType("req", i18nize("New Requirement Diagram"), (requirements,)),
    DiagramType("act", i18nize("New Activity Diagram"), (actions,)),
    DiagramType("sd", i18nize("New Sequence Diagram"), (interactions,)),
    DiagramType("stm", i18nize("New State Machine Diagram"), (states,)),
    DiagramType("uc", i18nize("New Use Case Diagram"), (use_cases,)),
)
