"""
This module contains the actions used in the Toolbox (lower left section
of the main window.

The Toolbox is bound to a diagram. When a diagram page (tab) is switched,
the actions bound to the toolbuttons should change as well.
"""

from typing import Optional, Sequence, Tuple

from gaphas.item import SE

from gaphor import UML, diagram
from gaphor.core import gettext
from gaphor.diagram.diagramtools import (
    DefaultTool,
    GroupPlacementTool,
    PlacementTool,
    TransactionalToolChain,
)
from gaphor.UML.event import DiagramItemCreated

__all__ = ["DiagramToolbox", "TOOLBOX_ACTIONS"]

# Actions: ((section (name, label, icon_name, shortcut)), ...)
TOOLBOX_ACTIONS: Sequence[Tuple[str, Sequence[Tuple[str, str, str, Optional[str]]]]] = (
    (
        gettext("General"),
        (
            (
                "toolbox-pointer",
                gettext("Pointer"),
                "gaphor-pointer-symbolic",
                "Escape",
            ),
            ("toolbox-line", gettext("Line"), "gaphor-line-symbolic", "l"),
            ("toolbox-box", gettext("Box"), "gaphor-box-symbolic", "b"),
            ("toolbox-ellipse", gettext("Ellipse"), "gaphor-ellipse-symbolic", "e"),
            ("toolbox-comment", gettext("Comment"), "gaphor-comment-symbolic", "k"),
            (
                "toolbox-comment-line",
                gettext("Comment line"),
                "gaphor-comment-line-symbolic",
                "<Shift>K",
            ),
        ),
    ),
    (
        gettext("Classes"),
        (
            ("toolbox-class", gettext("Class"), "gaphor-class-symbolic", "c"),
            (
                "toolbox-interface",
                gettext("Interface"),
                "gaphor-interface-symbolic",
                "i",
            ),
            ("toolbox-package", gettext("Package"), "gaphor-package-symbolic", "p"),
            (
                "toolbox-association",
                gettext("Association"),
                "gaphor-association-symbolic",
                "<Shift>A",
            ),
            (
                "toolbox-dependency",
                gettext("Dependency"),
                "gaphor-dependency-symbolic",
                "<Shift>D",
            ),
            (
                "toolbox-generalization",
                gettext("Generalization"),
                "gaphor-generalization-symbolic",
                "<Shift>G",
            ),
            (
                "toolbox-implementation",
                gettext("Implementation"),
                "gaphor-implementation-symbolic",
                "<Shift>I",
            ),
        ),
    ),
    (
        gettext("Components"),
        (
            (
                "toolbox-component",
                gettext("Component"),
                "gaphor-component-symbolic",
                "o",
            ),
            ("toolbox-artifact", gettext("Artifact"), "gaphor-artifact-symbolic", "h",),
            ("toolbox-node", gettext("Node"), "gaphor-node-symbolic", "n"),
            ("toolbox-device", gettext("Device"), "gaphor-device-symbolic", "d"),
            (
                "toolbox-connector",
                gettext("Connector"),
                "gaphor-connector-symbolic",
                "<Shift>C",
            ),
        ),
    ),
    (
        gettext("Actions"),
        (
            ("toolbox-action", gettext("Action"), "gaphor-action-symbolic", "a"),
            (
                "toolbox-initial-node",
                gettext("Initial node"),
                "gaphor-initial-node-symbolic",
                "j",
            ),
            (
                "toolbox-activity-final-node",
                gettext("Activity final node"),
                "gaphor-activity-final-node-symbolic",
                "f",
            ),
            (
                "toolbox-flow-final-node",
                gettext("Flow final node"),
                "gaphor-flow-final-node-symbolic",
                "w",
            ),
            (
                "toolbox-decision-node",
                gettext("Decision/merge node"),
                "gaphor-decision-node-symbolic",
                "g",
            ),
            (
                "toolbox-fork-node",
                gettext("Fork/join node"),
                "gaphor-fork-node-symbolic",
                "<Shift>R",
            ),
            (
                "toolbox-object-node",
                gettext("Object node"),
                "gaphor-object-node-symbolic",
                "<Shift>O",
            ),
            (
                "toolbox-partition",
                gettext("Partition"),
                "gaphor-partition-symbolic",
                "<Shift>P",
            ),
            (
                "toolbox-flow",
                gettext("Control/object flow"),
                "gaphor-control-flow-symbolic",
                "<Shift>F",
            ),
            (
                "toolbox-send-signal-action",
                gettext("Send signal action"),
                "gaphor-send-signal-action-symbolic",
                None,
            ),
            (
                "toolbox-accept-event-action",
                gettext("Accept event action"),
                "gaphor-accept-event-action-symbolic",
                None,
            ),
        ),
    ),
    (
        gettext("Interactions"),
        (
            ("toolbox-lifeline", gettext("Lifeline"), "gaphor-lifeline-symbolic", "v",),
            ("toolbox-message", gettext("Message"), "gaphor-message-symbolic", "M"),
            (
                "toolbox-interaction",
                gettext("Interaction"),
                "gaphor-interaction-symbolic",
                "<Shift>N",
            ),
        ),
    ),
    (
        gettext("States"),
        (
            ("toolbox-state", gettext("State"), "gaphor-state-symbolic", "s"),
            (
                "toolbox-initial-pseudostate",
                gettext("Initial Pseudostate"),
                "gaphor-initial-pseudostate-symbolic",
                "<Shift>S",
            ),
            (
                "toolbox-final-state",
                gettext("Final State"),
                "gaphor-final-state-symbolic",
                "x",
            ),
            (
                "toolbox-history-pseudostate",
                gettext("History Pseudostate"),
                "gaphor-pseudostate-symbolic",
                "q",
            ),
            (
                "toolbox-transition",
                gettext("Transition"),
                "gaphor-transition-symbolic",
                "<Shift>T",
            ),
        ),
    ),
    (
        gettext("Use Cases"),
        (
            ("toolbox-use-case", gettext("Use case"), "gaphor-use-case-symbolic", "u",),
            ("toolbox-actor", gettext("Actor"), "gaphor-actor-symbolic", "t"),
            (
                "toolbox-use-case-association",
                gettext("Association"),
                "gaphor-association-symbolic",
                "<Shift>B",
            ),
            (
                "toolbox-include",
                gettext("Include"),
                "gaphor-include-symbolic",
                "<Shift>U",
            ),
            (
                "toolbox-extend",
                gettext("Extend"),
                "gaphor-extend-symbolic",
                "<Shift>X",
            ),
        ),
    ),
    (
        gettext("Profiles"),
        (
            ("toolbox-profile", gettext("Profile"), "gaphor-profile-symbolic", "r"),
            (
                "toolbox-metaclass",
                gettext("Metaclass"),
                "gaphor-metaclass-symbolic",
                "m",
            ),
            (
                "toolbox-stereotype",
                gettext("Stereotype"),
                "gaphor-stereotype-symbolic",
                "z",
            ),
            (
                "toolbox-extension",
                gettext("Extension"),
                "gaphor-extension-symbolic",
                "<Shift>E",
            ),
        ),
    ),
)


def tooliter(toolbox_actions):
    """
    Iterate toolbox items, irregardless section headers
    """
    for name, section in toolbox_actions:
        yield from section


class DiagramToolbox:
    """
    Composite class for DiagramPage.

    See diagrampage.py.
    """

    def __init__(self, diagram, view, element_factory, event_manager):
        self.diagram = diagram
        self.view = view
        self.element_factory = element_factory
        self.event_manager = event_manager

    def get_tool(self, tool_name):
        """
        Return a tool associated with an id (action name).
        """
        return getattr(self, tool_name.replace("-", "_"))()

    action_list = list(zip(*list(tooliter(TOOLBOX_ACTIONS))))

    def _item_factory(self, item_class, subject_class=None, config_func=None):
        """
        ``config_func`` may be a function accepting the newly created item.
        """

        def factory_method(
            parent: Optional[UML.Presentation] = None,
        ) -> UML.Presentation:
            if subject_class:
                subject = self.element_factory.create(subject_class)
            else:
                subject = None
            item: UML.Presentation = self.diagram.create(
                item_class, subject=subject, parent=parent
            )
            if config_func:
                config_func(item)
            return item

        factory_method.item_class = item_class  # type: ignore[attr-defined] # noqa: F821
        return factory_method

    def _namespace_config(self, new_item):
        subject = new_item.subject
        subject.package = self.diagram.namespace
        subject.name = f"New{type(subject).__name__}"

    # TODO: Move the event handling in placement tool. Let it depend on event_manager.
    def _after_handler(self, new_item):
        self.event_manager.handle(DiagramItemCreated(self.element_factory, new_item))

    ##
    ## Toolbox actions
    ##

    def toolbox_pointer(self):
        if self.view:
            return DefaultTool(self.event_manager)

    # @tool(diagram.general.Line, "toolbox-line", gettext("Line"), "gaphor-line-symbolic", "l")
    def toolbox_line(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.general.Line),
            after_handler=self._after_handler,
        )

    def toolbox_box(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.general.Box),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_ellipse(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.general.Ellipse),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_comment(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.general.CommentItem, UML.Comment),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_comment_line(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.general.CommentLineItem),
            after_handler=self._after_handler,
        )

    # Classes:

    def toolbox_class(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.classes.ClassItem, UML.Class, config_func=self._namespace_config
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_interface(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.classes.InterfaceItem,
                UML.Interface,
                config_func=self._namespace_config,
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_package(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.classes.PackageItem,
                UML.Package,
                config_func=self._namespace_config,
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_association(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.classes.AssociationItem),
            after_handler=self._after_handler,
        )

    def toolbox_dependency(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.classes.DependencyItem),
            after_handler=self._after_handler,
        )

    def toolbox_generalization(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.classes.GeneralizationItem),
            after_handler=self._after_handler,
        )

    def toolbox_implementation(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.classes.ImplementationItem),
            after_handler=self._after_handler,
        )

    # Components:

    def toolbox_component(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.components.ComponentItem,
                UML.Component,
                config_func=self._namespace_config,
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_artifact(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.components.ArtifactItem,
                UML.Artifact,
                config_func=self._namespace_config,
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_node(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.components.NodeItem,
                UML.Node,
                config_func=self._namespace_config,
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_device(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.components.NodeItem,
                UML.Device,
                config_func=self._namespace_config,
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_connector(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.components.ConnectorItem),
            after_handler=self._after_handler,
        )

    # Actions:

    def toolbox_action(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.actions.ActionItem,
                UML.Action,
                config_func=self._namespace_config,
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_send_signal_action(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.actions.SendSignalActionItem,
                UML.SendSignalAction,
                config_func=self._namespace_config,
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_accept_event_action(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.actions.AcceptEventActionItem,
                UML.AcceptEventAction,
                config_func=self._namespace_config,
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_initial_node(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.actions.InitialNodeItem, UML.InitialNode
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_activity_final_node(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.actions.ActivityFinalNodeItem, UML.ActivityFinalNode
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_flow_final_node(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.actions.FlowFinalNodeItem, UML.FlowFinalNode
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_decision_node(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.actions.DecisionNodeItem, UML.DecisionNode
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_fork_node(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.actions.ForkNodeItem, UML.JoinNode),
            handle_index=1,
            after_handler=self._after_handler,
        )

    def toolbox_object_node(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.actions.ObjectNodeItem,
                UML.ObjectNode,
                config_func=self._namespace_config,
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_partition(self):
        # note no subject, which is created by grouping adapter
        return GroupPlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.actions.PartitionItem),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_flow(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.actions.FlowItem),
            after_handler=self._after_handler,
        )

    # Interactions:
    def toolbox_interaction(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.interactions.InteractionItem,
                UML.Interaction,
                config_func=self._namespace_config,
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_lifeline(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.interactions.LifelineItem,
                UML.Lifeline,
                config_func=self._namespace_config,
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_message(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.interactions.MessageItem),
            after_handler=self._after_handler,
        )

    # States:
    def toolbox_state(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.states.StateItem, UML.State, config_func=self._namespace_config
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_initial_pseudostate(self):
        def set_state(item):
            item.subject.kind = "initial"

        return PlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.states.InitialPseudostateItem, UML.Pseudostate, set_state
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_history_pseudostate(self):
        def set_state(item):
            item.subject.kind = "shallowHistory"

        return PlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.states.HistoryPseudostateItem, UML.Pseudostate, set_state
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_final_state(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.states.FinalStateItem, UML.FinalState
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_transition(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.states.TransitionItem),
            after_handler=self._after_handler,
        )

    # Use cases:

    def toolbox_use_case(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.usecases.UseCaseItem,
                UML.UseCase,
                config_func=self._namespace_config,
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_actor(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.usecases.ActorItem,
                UML.Actor,
                config_func=self._namespace_config,
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_use_case_association(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.classes.AssociationItem),
            after_handler=self._after_handler,
        )

    def toolbox_include(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.usecases.IncludeItem),
            after_handler=self._after_handler,
        )

    def toolbox_extend(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.usecases.ExtendItem),
            after_handler=self._after_handler,
        )

    # Profiles:

    def toolbox_profile(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.classes.PackageItem,
                UML.Profile,
                config_func=self._namespace_config,
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_metaclass(self):
        def metaclass_config(new_item):
            self._namespace_config(new_item)
            new_item.subject.name = "Class"

        return PlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.classes.ClassItem, UML.Class, config_func=metaclass_config
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_stereotype(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.classes.ClassItem,
                UML.Stereotype,
                config_func=self._namespace_config,
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_extension(self):
        return PlacementTool(
            self.view,
            item_factory=self._item_factory(diagram.profiles.ExtensionItem),
            after_handler=self._after_handler,
        )
