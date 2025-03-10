"""The action definition for the SysML toolbox."""

from gaphor import UML
from gaphor.diagram.diagramtoolbox import (
    DiagramType,
    DiagramTypes,
    ElementCreateInfo,
    ToolboxDefinition,
    ToolDef,
    ToolSection,
    new_item_factory,
)
from gaphor.i18n import gettext, i18nize
from gaphor.SysML import diagramitems as sysml_items
from gaphor.SysML.allocations.allocationstoolbox import allocations
from gaphor.SysML.blocks.blockstoolbox import blocks
from gaphor.SysML.diagramtype import DiagramDefault, SysMLDiagramType
from gaphor.SysML.requirements.requirementstoolbox import requirements
from gaphor.SysML.sysml import (
    ActivityDiagram,
    Block,
    BlockDefinitionDiagram,
    ConstraintBlock,
    InterfaceBlock,
    InternalBlockDiagram,
    PackageDiagram,
    Requirement,
    RequirementDiagram,
    SequenceDiagram,
    StateMachineDiagram,
    UseCaseDiagram,
    ValueType,
)
from gaphor.UML import diagramitems as uml_items
from gaphor.UML.actions.actionstoolbox import actions
from gaphor.UML.general.generaltoolbox import general_tools
from gaphor.UML.interactions.interactionstoolbox import interactions
from gaphor.UML.states.statestoolbox import states
from gaphor.UML.toolboxconfig import named_element_config
from gaphor.UML.uml import (
    Activity,
    Actor,
    Enumeration,
    Interaction,
    Package,
    StateMachine,
    UseCase,
)
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
            "gaphor-proxy-port-symbolic",
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
    allocations,
)

root = type(None)

# Not implemented: Parameter Diagram
sysml_diagram_types: DiagramTypes = (
    SysMLDiagramType(
        BlockDefinitionDiagram,
        i18nize("Block Definition Diagram"),
        (blocks,),
        (Block, Package, ConstraintBlock, Activity),
        (DiagramDefault(root, Package, i18nize("New Package")),),
    ),
    SysMLDiagramType(
        InternalBlockDiagram,
        i18nize("Internal Block Diagram"),
        (internal_blocks,),
        (
            Block,
            ConstraintBlock,
        ),
        (
            DiagramDefault(Package, Block, i18nize("New Block")),
            DiagramDefault(root, Block, i18nize("New Block")),
        ),
    ),
    SysMLDiagramType(
        PackageDiagram,
        i18nize("Package Diagram"),
        (blocks,),
        (Package,),  # model, modelLibrary, profile
        (DiagramDefault(root, Package, i18nize("New Package")),),
    ),
    SysMLDiagramType(
        RequirementDiagram,
        i18nize("Requirement Diagram"),
        (requirements,),
        (
            Package,
            Requirement,
            # model,
            # modelLibrary
        ),
        (DiagramDefault(root, Package, i18nize("New Package")),),
    ),
    SysMLDiagramType(
        ActivityDiagram,
        i18nize("Activity Diagram"),
        (actions,),
        (Activity,),
        (
            DiagramDefault(Package, Activity, i18nize("New Activity")),
            DiagramDefault(root, Activity, i18nize("New Activity")),
        ),
    ),
    SysMLDiagramType(
        SequenceDiagram,
        i18nize("Sequence Diagram"),
        (interactions,),
        (Interaction,),
        (
            DiagramDefault(Package, Interaction, i18nize("New Interaction")),
            DiagramDefault(root, Interaction, i18nize("New Interaction")),
        ),
    ),
    SysMLDiagramType(
        StateMachineDiagram,
        i18nize("State Machine Diagram"),
        (states,),
        (StateMachine,),
        (
            DiagramDefault(Package, StateMachine, i18nize("New State Machine")),
            DiagramDefault(root, StateMachine, i18nize("New State Machine")),
        ),
    ),
    SysMLDiagramType(
        UseCaseDiagram,
        i18nize("Use Case Diagram"),
        (use_cases,),
        (
            Package,
            Block,
            # model,
            # modelLibrary
        ),
        (DiagramDefault(root, Package, i18nize("New Package")),),
    ),
    DiagramType(UML.Diagram, i18nize("Generic Diagram"), ()),
)

sysml_element_types = (
    ElementCreateInfo("package", i18nize("Package"), Package, (Package,)),
    ElementCreateInfo("activity", i18nize("Activity"), Activity, (Package,)),
    ElementCreateInfo("actor", i18nize("Actor"), Actor, (Package,)),
    ElementCreateInfo("block", i18nize("Block"), Block, (Package,)),
    ElementCreateInfo("enumeration", i18nize("Enumeration"), Enumeration, (Package,)),
    ElementCreateInfo("interaction", i18nize("Interaction"), Interaction, (Package,)),
    ElementCreateInfo(
        "interfaceblock", i18nize("Interface Block"), InterfaceBlock, (Package,)
    ),
    ElementCreateInfo(
        "requirement",
        i18nize("Requirement"),
        Requirement,
        (
            Package,
            Requirement,
        ),
    ),
    ElementCreateInfo(
        "statemachine", i18nize("State Machine"), StateMachine, (Package,)
    ),
    ElementCreateInfo("usecase", i18nize("Use Case"), UseCase, (Package,)),
    ElementCreateInfo("valuetype", i18nize("Value Type"), ValueType, (Package,)),
)
