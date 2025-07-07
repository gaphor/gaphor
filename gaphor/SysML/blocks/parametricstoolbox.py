"""The definition for the parametric section of the toolbox."""

from gaphor.core import gettext
from gaphor.diagram.diagramtoolbox import ToolDef, ToolSection, new_item_factory
from gaphor.SysML import diagramitems as sysml_items
from gaphor.SysML import sysml
from gaphor.UML import diagramitems as uml_items
from gaphor.UML.toolboxconfig import named_element_config

parametric_blocks = ToolSection(
    gettext("Parametric Blocks"),
    (
        ToolDef(
            "toolbox-connector",
            gettext("Connector"),
            "gaphor-connector-symbolic",
            None,
            new_item_factory(uml_items.ConnectorItem),
        ),
        ToolDef(
            "toolbox-constraint-block",
            gettext("Constraint Block"),
            "gaphor-constraint-block-symbolic",
            None,
            new_item_factory(
                sysml_items.ConstraintItem,
                sysml.Constraint,
                config_func=named_element_config,
            ),
        ),
    ),
)
