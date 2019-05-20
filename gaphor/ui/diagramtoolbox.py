"""
This module contains the actions used in the Toolbox (lower left section
of the main window.

The Toolbox is bound to a diagram. When a diagram page (tab) is switched,
the actions bound to the toolbuttons should change as well.
"""

from gaphas.item import SE

from gaphor import UML
from gaphor.UML.event import DiagramItemCreateEvent
from gaphor.core import _, inject, radio_action, build_action_group
from gaphor import diagram
from gaphor.ui.diagramtools import PlacementTool, GroupPlacementTool, DefaultTool

__all__ = ["DiagramToolbox", "TOOLBOX_ACTIONS"]

# Actions: ((section (name, label, stock_id, shortcut)), ...)
TOOLBOX_ACTIONS = (
    (
        _("General"),
        (
            ("toolbox-pointer", _("Pointer"), "gaphor-pointer", "Escape"),
            ("toolbox-line", _("Line"), "gaphor-line", "l"),
            ("toolbox-box", _("Box"), "gaphor-box", "b"),
            ("toolbox-ellipse", _("Ellipse"), "gaphor-ellipse", "e"),
            ("toolbox-comment", _("Comment"), "gaphor-comment", "k"),
            ("toolbox-comment-line", _("Comment line"), "gaphor-comment-line", "K"),
        ),
    ),
    (
        _("Classes"),
        (
            ("toolbox-class", _("Class"), "gaphor-class", "c"),
            ("toolbox-interface", _("Interface"), "gaphor-interface", "i"),
            ("toolbox-package", _("Package"), "gaphor-package", "p"),
            ("toolbox-association", _("Association"), "gaphor-association", "A"),
            ("toolbox-dependency", _("Dependency"), "gaphor-dependency", "D"),
            (
                "toolbox-generalization",
                _("Generalization"),
                "gaphor-generalization",
                "G",
            ),
            (
                "toolbox-implementation",
                _("Implementation"),
                "gaphor-implementation",
                "I",
            ),
        ),
    ),
    (
        _("Components"),
        (
            ("toolbox-component", _("Component"), "gaphor-component", "o"),
            ("toolbox-artifact", _("Artifact"), "gaphor-artifact", "h"),
            ("toolbox-node", _("Node"), "gaphor-node", "n"),
            ("toolbox-device", _("Device"), "gaphor-device", "d"),
            ("toolbox-subsystem", _("Subsystem"), "gaphor-subsystem", "y"),
            ("toolbox-connector", _("Connector"), "gaphor-connector", "C"),
        ),
    ),
    (
        _("Actions"),
        (
            ("toolbox-action", _("Action"), "gaphor-action", "a"),
            ("toolbox-initial-node", _("Initial node"), "gaphor-initial-node", "j"),
            (
                "toolbox-activity-final-node",
                _("Activity final node"),
                "gaphor-activity-final-node",
                "f",
            ),
            (
                "toolbox-flow-final-node",
                _("Flow final node"),
                "gaphor-flow-final-node",
                "w",
            ),
            (
                "toolbox-decision-node",
                _("Decision/merge node"),
                "gaphor-decision-node",
                "g",
            ),
            ("toolbox-fork-node", _("Fork/join node"), "gaphor-fork-node", "R"),
            ("toolbox-object-node", _("Object node"), "gaphor-object-node", "O"),
            ("toolbox-partition", _("Partition"), "gaphor-partition", "P"),
            ("toolbox-flow", _("Control/object flow"), "gaphor-control-flow", "F"),
            (
                "toolbox-send-signal-action",
                _("Send signal action"),
                "gaphor-send-signal-action",
                None,
            ),
            (
                "toolbox-accept-event-action",
                _("Accept event action"),
                "gaphor-accept-event-action",
                None,
            ),
        ),
    ),
    (
        _("Interactions"),
        (
            ("toolbox-lifeline", _("Lifeline"), "gaphor-lifeline", "v"),
            ("toolbox-message", _("Message"), "gaphor-message", "M"),
            ("toolbox-interaction", _("Interaction"), "gaphor-interaction", "N"),
        ),
    ),
    (
        _("States"),
        (
            ("toolbox-state", _("State"), "gaphor-state", "s"),
            (
                "toolbox-initial-pseudostate",
                _("Initial Pseudostate"),
                "gaphor-initial-pseudostate",
                "S",
            ),
            ("toolbox-final-state", _("Final State"), "gaphor-final-state", "x"),
            (
                "toolbox-history-pseudostate",
                _("History Pseudostate"),
                "gaphor-history-pseudostate",
                "q",
            ),
            ("toolbox-transition", _("Transition"), "gaphor-transition", "T"),
        ),
    ),
    (
        _("Use Cases"),
        (
            ("toolbox-usecase", _("Use case"), "gaphor-usecase", "u"),
            ("toolbox-actor", _("Actor"), "gaphor-actor", "t"),
            (
                "toolbox-usecase-association",
                _("Association"),
                "gaphor-association",
                "B",
            ),
            ("toolbox-include", _("Include"), "gaphor-include", "U"),
            ("toolbox-extend", _("Extend"), "gaphor-extend", "X"),
        ),
    ),
    (
        _("Profiles"),
        (
            ("toolbox-profile", _("Profile"), "gaphor-profile", "r"),
            ("toolbox-metaclass", _("Metaclass"), "gaphor-metaclass", "m"),
            ("toolbox-stereotype", _("Stereotype"), "gaphor-stereotype", "z"),
            ("toolbox-extension", _("Extension"), "gaphor-extension", "E"),
        ),
    ),
)


def itemiter(toolbox_actions):
    """
    Iterate toolbox items, irregardless section headers
    """
    for name, section in toolbox_actions:
        for e in section:
            yield e


class DiagramToolbox:
    """
    Composite class for DiagramPage (diagrampage.py).
    """

    element_factory = inject("element_factory")
    event_manager = inject("event_manager")
    properties = inject("properties")

    def __init__(self, diagram, view):
        self.view = view
        self.diagram = diagram
        self.action_group = build_action_group(self)

    namespace = property(lambda s: s.diagram.namespace)

    def get_tool(self, tool_name):
        """
        Return a tool associated with an id (action name).
        """
        return getattr(self, tool_name.replace("-", "_"))()

    action_list = list(zip(*list(itemiter(TOOLBOX_ACTIONS))))

    @radio_action(names=action_list[0], labels=action_list[1], stock_ids=action_list[2])
    def _set_toolbox_action(self, id):
        """
        Activate a tool based on its index in the TOOLBOX_ACTIONS list.
        """
        tool_name = list(itemiter(TOOLBOX_ACTIONS))[id][0]
        self.view.tool = self.get_tool(tool_name)

    def _item_factory(self, item_class, subject_class=None, config_func=None):
        """
        ``config_func`` may be a function accepting the newly created item.
        """

        def factory_method(parent=None):
            if subject_class:
                subject = self.element_factory.create(subject_class)
            else:
                subject = None
            item = self.diagram.create(item_class, subject=subject, parent=parent)
            if config_func:
                config_func(item)
            return item

        factory_method.item_class = item_class
        return factory_method

    def _namespace_item_factory(
        self, item_class, subject_class, stereotype=None, name=None
    ):
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
            elif stereotype:
                subject.name = "New%s" % stereotype.capitalize()
            else:
                subject.name = "New%s" % subject_class.__name__
            return item

        factory_method.item_class = item_class
        return factory_method

    def _after_handler(self, new_item):
        if self.properties("reset-tool-after-create", False):
            self.action_group.get_action("toolbox-pointer").activate()
        self.event_manager.handle(
            DiagramItemCreateEvent(self.element_factory, new_item)
        )

    ##
    ## Toolbox actions
    ##

    def toolbox_pointer(self):
        if self.view:
            return DefaultTool()

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

    def toolbox_subsystem(self):
        return GroupPlacementTool(
            self.view,
            item_factory=self._namespace_item_factory(
                diagram.components.SubsystemItem, UML.Component, "subsystem"
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

    def toolbox_usecase(self):
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

    def toolbox_usecase_association(self):
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
                diagram.profiles.MetaclassItem, UML.Class, "metaclass", name="Class"
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
