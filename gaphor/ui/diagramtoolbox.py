"""
This module contains the actions used in the Toolbox (lower left section
of the main window.

The Toolbox is bound to a diagram. When a diagram page (tab) is switched,
the actions bound to the toolbuttons should change as well.
"""

from typing import Optional, Sequence, Tuple

from gaphas.item import SE

from gaphor import UML, diagram
from gaphor.core import translate
from gaphor.ui.diagramtools import (
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
        translate("General"),
        (
            (
                "toolbox-pointer",
                translate("Pointer"),
                "gaphor-pointer-symbolic",
                "Escape",
            ),
            ("toolbox-line", translate("Line"), "gaphor-line-symbolic", "l"),
            ("toolbox-box", translate("Box"), "gaphor-box-symbolic", "b"),
            ("toolbox-ellipse", translate("Ellipse"), "gaphor-ellipse-symbolic", "e"),
            ("toolbox-comment", translate("Comment"), "gaphor-comment-symbolic", "k"),
            (
                "toolbox-comment-line",
                translate("Comment line"),
                "gaphor-comment-line-symbolic",
                "<Shift>K",
            ),
        ),
    ),
    (
        translate("Classes"),
        (
            ("toolbox-class", translate("Class"), "gaphor-class-symbolic", "c"),
            (
                "toolbox-interface",
                translate("Interface"),
                "gaphor-interface-symbolic",
                "i",
            ),
            ("toolbox-package", translate("Package"), "gaphor-package-symbolic", "p"),
            (
                "toolbox-association",
                translate("Association"),
                "gaphor-association-symbolic",
                "<Shift>A",
            ),
            (
                "toolbox-dependency",
                translate("Dependency"),
                "gaphor-dependency-symbolic",
                "<Shift>D",
            ),
            (
                "toolbox-generalization",
                translate("Generalization"),
                "gaphor-generalization-symbolic",
                "<Shift>G",
            ),
            (
                "toolbox-implementation",
                translate("Implementation"),
                "gaphor-implementation-symbolic",
                "<Shift>I",
            ),
        ),
    ),
    (
        translate("Components"),
        (
            (
                "toolbox-component",
                translate("Component"),
                "gaphor-component-symbolic",
                "o",
            ),
            (
                "toolbox-artifact",
                translate("Artifact"),
                "gaphor-artifact-symbolic",
                "h",
            ),
            ("toolbox-node", translate("Node"), "gaphor-node-symbolic", "n"),
            ("toolbox-device", translate("Device"), "gaphor-device-symbolic", "d"),
            (
                "toolbox-connector",
                translate("Connector"),
                "gaphor-connector-symbolic",
                "<Shift>C",
            ),
        ),
    ),
    (
        translate("Actions"),
        (
            ("toolbox-action", translate("Action"), "gaphor-action-symbolic", "a"),
            (
                "toolbox-initial-node",
                translate("Initial node"),
                "gaphor-initial-node-symbolic",
                "j",
            ),
            (
                "toolbox-activity-final-node",
                translate("Activity final node"),
                "gaphor-activity-final-node-symbolic",
                "f",
            ),
            (
                "toolbox-flow-final-node",
                translate("Flow final node"),
                "gaphor-flow-final-node-symbolic",
                "w",
            ),
            (
                "toolbox-decision-node",
                translate("Decision/merge node"),
                "gaphor-decision-node-symbolic",
                "g",
            ),
            (
                "toolbox-fork-node",
                translate("Fork/join node"),
                "gaphor-fork-node-symbolic",
                "<Shift>R",
            ),
            (
                "toolbox-object-node",
                translate("Object node"),
                "gaphor-object-node-symbolic",
                "<Shift>O",
            ),
            (
                "toolbox-partition",
                translate("Partition"),
                "gaphor-partition-symbolic",
                "<Shift>P",
            ),
            (
                "toolbox-flow",
                translate("Control/object flow"),
                "gaphor-control-flow-symbolic",
                "<Shift>F",
            ),
            (
                "toolbox-send-signal-action",
                translate("Send signal action"),
                "gaphor-send-signal-action-symbolic",
                None,
            ),
            (
                "toolbox-accept-event-action",
                translate("Accept event action"),
                "gaphor-accept-event-action-symbolic",
                None,
            ),
        ),
    ),
    (
        translate("Interactions"),
        (
            (
                "toolbox-lifeline",
                translate("Lifeline"),
                "gaphor-lifeline-symbolic",
                "v",
            ),
            ("toolbox-message", translate("Message"), "gaphor-message-symbolic", "M"),
            (
                "toolbox-interaction",
                translate("Interaction"),
                "gaphor-interaction-symbolic",
                "<Shift>N",
            ),
        ),
    ),
    (
        translate("States"),
        (
            ("toolbox-state", translate("State"), "gaphor-state-symbolic", "s"),
            (
                "toolbox-initial-pseudostate",
                translate("Initial Pseudostate"),
                "gaphor-initial-pseudostate-symbolic",
                "<Shift>S",
            ),
            (
                "toolbox-final-state",
                translate("Final State"),
                "gaphor-final-state-symbolic",
                "x",
            ),
            (
                "toolbox-history-pseudostate",
                translate("History Pseudostate"),
                "gaphor-pseudostate-symbolic",
                "q",
            ),
            (
                "toolbox-transition",
                translate("Transition"),
                "gaphor-transition-symbolic",
                "<Shift>T",
            ),
        ),
    ),
    (
        translate("Use Cases"),
        (
            (
                "toolbox-use-case",
                translate("Use case"),
                "gaphor-use-case-symbolic",
                "u",
            ),
            ("toolbox-actor", translate("Actor"), "gaphor-actor-symbolic", "t"),
            (
                "toolbox-use-case-association",
                translate("Association"),
                "gaphor-association-symbolic",
                "<Shift>B",
            ),
            (
                "toolbox-include",
                translate("Include"),
                "gaphor-include-symbolic",
                "<Shift>U",
            ),
            (
                "toolbox-extend",
                translate("Extend"),
                "gaphor-extend-symbolic",
                "<Shift>X",
            ),
        ),
    ),
    (
        translate("Profiles"),
        (
            ("toolbox-profile", translate("Profile"), "gaphor-profile-symbolic", "r"),
            (
                "toolbox-metaclass",
                translate("Metaclass"),
                "gaphor-metaclass-symbolic",
                "m",
            ),
            (
                "toolbox-stereotype",
                translate("Stereotype"),
                "gaphor-stereotype-symbolic",
                "z",
            ),
            (
                "toolbox-extension",
                translate("Extension"),
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

    namespace = property(lambda s: s.diagram.namespace)

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

        factory_method.item_class = item_class  # type: ignore[attr-defined]
        return factory_method

    def _namespace_item_factory(self, item_class, subject_class, name=None):
        """
        Returns a factory method for Namespace classes.
        To be used by the PlacementTool.
        """

        def factory_method(parent=None):
            subject = self.element_factory.create(subject_class)
            item = self.diagram.create(item_class, subject=subject, parent=parent)
            subject.package = self.namespace
            if name is not None:
                subject.name = name
            else:
                subject.name = f"New{subject_class.__name__}"
            return item

        factory_method.item_class = item_class  # type: ignore[attr-defined]
        return factory_method

    def _after_handler(self, new_item):
        self.event_manager.handle(DiagramItemCreated(self.element_factory, new_item))

    ##
    ## Toolbox actions
    ##

    def toolbox_pointer(self):
        if self.view:
            return DefaultTool(self.event_manager)

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
            item_factory=self._namespace_item_factory(
                diagram.classes.ClassItem, UML.Class
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_interface(self):
        return PlacementTool(
            self.view,
            item_factory=self._namespace_item_factory(
                diagram.classes.InterfaceItem, UML.Interface
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_package(self):
        return PlacementTool(
            self.view,
            item_factory=self._namespace_item_factory(
                diagram.classes.PackageItem, UML.Package
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
            item_factory=self._namespace_item_factory(
                diagram.components.ComponentItem, UML.Component
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_artifact(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._namespace_item_factory(
                diagram.components.ArtifactItem, UML.Artifact
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_node(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._namespace_item_factory(
                diagram.components.NodeItem, UML.Node
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_device(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._namespace_item_factory(
                diagram.components.NodeItem, UML.Device
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
            item_factory=self._namespace_item_factory(
                diagram.actions.ActionItem, UML.Action
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_send_signal_action(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._namespace_item_factory(
                diagram.actions.SendSignalActionItem, UML.SendSignalAction
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_accept_event_action(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._namespace_item_factory(
                diagram.actions.AcceptEventActionItem, UML.AcceptEventAction
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
            item_factory=self._namespace_item_factory(
                diagram.actions.ObjectNodeItem, UML.ObjectNode
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
            item_factory=self._namespace_item_factory(
                diagram.interactions.InteractionItem, UML.Interaction
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_lifeline(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._namespace_item_factory(
                diagram.interactions.LifelineItem, UML.Lifeline
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
            item_factory=self._namespace_item_factory(
                diagram.states.StateItem, UML.State
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def _toolbox_pseudostate(self, kind):
        def set_state(item):
            item.subject.kind = kind

        return PlacementTool(
            self.view,
            item_factory=self._item_factory(
                diagram.states.InitialPseudostateItem, UML.Pseudostate, set_state
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
            item_factory=self._namespace_item_factory(
                diagram.usecases.UseCaseItem, UML.UseCase
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_actor(self):
        return PlacementTool(
            self.view,
            item_factory=self._namespace_item_factory(
                diagram.usecases.ActorItem, UML.Actor
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
            item_factory=self._namespace_item_factory(
                diagram.classes.PackageItem, UML.Profile
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_metaclass(self):
        return PlacementTool(
            self.view,
            item_factory=self._namespace_item_factory(
                diagram.classes.ClassItem, UML.Class, name="Class"
            ),
            handle_index=SE,
            after_handler=self._after_handler,
        )

    def toolbox_stereotype(self):
        return PlacementTool(
            self.view,
            item_factory=self._namespace_item_factory(
                diagram.classes.ClassItem, UML.Stereotype
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
