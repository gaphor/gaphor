"""Flow item adapter connections."""

from typing import Type, Union

from gaphor import UML
from gaphor.diagram.connectors import Connector, RelationshipConnect
from gaphor.diagram.support import get_diagram_item_metadata, get_model_element
from gaphor.UML.actions.action import (
    AcceptEventActionItem,
    ActionItem,
    SendSignalActionItem,
)
from gaphor.UML.actions.activity import ActivityParameterNodeItem
from gaphor.UML.actions.activitynodes import (
    ActivityNodeItem,
    DecisionNodeItem,
    ForkNodeItem,
)
from gaphor.UML.actions.flow import ControlFlowItem, ObjectFlowItem
from gaphor.UML.actions.objectnode import ObjectNodeItem
from gaphor.UML.actions.pin import InputPinItem, OutputPinItem


class FlowConnect(RelationshipConnect):
    """Connect FlowItem and Action, initial/final nodes."""

    line: Union[ControlFlowItem, ObjectFlowItem]

    def allow(self, handle, port):
        line = self.line
        subject = self.element.subject

        if (
            handle is line.head
            and isinstance(subject, (UML.FinalNode, UML.InputPin))
            or handle is line.tail
            and isinstance(subject, (UML.InitialNode, UML.OutputPin))
        ):
            return False

        # Flow type specific constraints:
        if isinstance(line, ControlFlowItem) and isinstance(subject, UML.ObjectNode):
            return False

        if isinstance(line, ObjectFlowItem):
            opposite_handle = line.opposite(handle)
            opposite_item = self.get_connected(opposite_handle)
            opposite_subject = opposite_item.subject if opposite_item else None
            if isinstance(subject, UML.ExecutableNode) and isinstance(
                opposite_subject, UML.ExecutableNode
            ):
                return False

        return super().allow(handle, port)

    def connect_subject(self, handle):
        line = self.line
        assert line

        c1 = self.get_connected(line.head)
        c2 = self.get_connected(line.tail)
        assert c1 and c2
        assert isinstance(c1.subject, UML.ActivityNode)

        element_type = get_model_element(type(line))
        metadata = get_diagram_item_metadata(type(line))
        relation: Union[UML.ControlFlow, UML.ObjectFlow] = self.relationship_or_new(
            element_type, metadata["head"], metadata["tail"]
        )

        line.subject = relation
        if c1.subject.activity:
            relation.activity = c1.subject.activity
        elif isinstance(c1.subject, UML.OutputPin) and c1.subject.owner:
            relation.activity = c1.subject.owner.activity  # type: ignore[attr-defined]
        elif isinstance(c2.subject, UML.InputPin) and c2.subject.owner:
            relation.activity = c2.subject.owner.activity  # type: ignore[attr-defined]

        opposite = line.opposite(handle)
        otc = self.get_connected(opposite)
        if (
            opposite
            and (isinstance(line, (ControlFlowItem, ObjectFlowItem)))
            and isinstance(otc, (ForkNodeItem, DecisionNodeItem))
        ):
            adapter = Connector(otc, line)
            adapter.combine_nodes()

    def disconnect_subject(self, handle):
        super().disconnect_subject(handle)
        line = self.line
        opposite = line.opposite(handle)
        otc = self.get_connected(opposite)
        if (
            opposite
            and (isinstance(line, (ControlFlowItem, ObjectFlowItem)))
            and isinstance(otc, (ForkNodeItem, DecisionNodeItem))
        ):
            adapter = Connector(otc, line)
            adapter.decombine_nodes()


Connector.register(ActionItem, ControlFlowItem)(FlowConnect)
Connector.register(ActivityNodeItem, ControlFlowItem)(FlowConnect)
Connector.register(SendSignalActionItem, ControlFlowItem)(FlowConnect)
Connector.register(AcceptEventActionItem, ControlFlowItem)(FlowConnect)

Connector.register(ActionItem, ObjectFlowItem)(FlowConnect)
Connector.register(ActivityNodeItem, ObjectFlowItem)(FlowConnect)
Connector.register(SendSignalActionItem, ObjectFlowItem)(FlowConnect)

Connector.register(ObjectNodeItem, ObjectFlowItem)(FlowConnect)
Connector.register(ActivityParameterNodeItem, ObjectFlowItem)(FlowConnect)
Connector.register(InputPinItem, ObjectFlowItem)(FlowConnect)
Connector.register(OutputPinItem, ObjectFlowItem)(FlowConnect)


class FlowForkDecisionNodeFlowConnect(FlowConnect):
    """Abstract class with common behaviour for Fork/Join node and
    Decision/Merge node."""

    element: Union[ForkNodeItem, DecisionNodeItem]
    fork_node_cls: Type[UML.ControlNode]
    join_node_cls: Type[UML.ControlNode]

    def allow(self, handle, port):
        # No cyclic connect is possible on a Flow/Decision node:
        head, tail = self.line.head, self.line.tail
        subject = self.element.subject

        hct = self.get_connected(head)
        tct = self.get_connected(tail)
        if (
            handle is head
            and tct
            and tct.subject is subject
            or handle is tail
            and hct
            and hct.subject is subject
        ):
            return None

        return super().allow(handle, port)

    def combine_nodes(self):
        """Combine join/fork or decision/merge nodes into one diagram item."""
        fork_node_cls = self.fork_node_cls
        join_node_cls = self.join_node_cls
        element = self.element
        subject = element.subject
        if len(subject.incoming) > 1 and len(subject.outgoing) < 2:
            UML.recipes.swap_element(subject, join_node_cls)
            element.request_update()
        elif len(subject.incoming) < 2 and len(subject.outgoing) > 1:
            UML.recipes.swap_element(subject, fork_node_cls)
            element.request_update()
        elif (
            not element.combined
            and len(subject.incoming) > 1
            and len(subject.outgoing) > 1
        ):
            join_node = subject

            # determine flow class:
            flow_class = (
                UML.ObjectFlow
                if any(f for f in join_node.incoming if isinstance(f, UML.ObjectFlow))
                else UML.ControlFlow
            )

            UML.recipes.swap_element(join_node, join_node_cls)
            fork_node: UML.ControlNode = element.model.create(fork_node_cls)
            for flow in list(join_node.outgoing):
                flow.source = fork_node
            flow = element.model.create(flow_class)
            flow.source = join_node
            flow.target = fork_node

            element.combined = fork_node

    def decombine_nodes(self):
        """Decombine join/fork or decision/merge nodes."""
        element = self.element
        if element.combined:
            join_node = element.subject
            cflow = join_node.outgoing[0]  # combining flow
            fork_node = cflow.target
            assert fork_node is element.combined
            join_node_cls = self.join_node_cls
            assert isinstance(join_node, join_node_cls)
            fork_node_cls = self.fork_node_cls
            assert isinstance(fork_node, fork_node_cls)

            if len(join_node.incoming) < 2 or len(fork_node.outgoing) < 2:
                # Move all outgoing edges to the first node (the join node):
                for f in list(fork_node.outgoing):
                    f.source = join_node
                cflow.unlink()
                fork_node.unlink()
                # swap subject to fork node if outgoing > 1
                if len(join_node.outgoing) > 1:
                    assert len(join_node.incoming) < 2
                    UML.recipes.swap_element(join_node, fork_node_cls)
                del element.combined

    def connect_subject(self, handle):
        """In addition to a subject connect, the subject of the element may be
        changed.

        For readability, parameters are named after the classes used by
        Join/Fork nodes.
        """
        super().connect_subject(handle)

        # Switch class for self.element Join/Fork depending on the number
        # of incoming/outgoing edges.
        self.combine_nodes()

    def disconnect_subject(self, handle):
        super().disconnect_subject(handle)
        if self.element.combined:
            self.decombine_nodes()


@Connector.register(ForkNodeItem, ControlFlowItem)
@Connector.register(ForkNodeItem, ObjectFlowItem)
class FlowForkNodeFlowConnect(FlowForkDecisionNodeFlowConnect):
    """Connect Flow to a ForkNode."""

    fork_node_cls = UML.ForkNode
    join_node_cls = UML.JoinNode


@Connector.register(DecisionNodeItem, ControlFlowItem)
@Connector.register(DecisionNodeItem, ObjectFlowItem)
class FlowDecisionNodeFlowConnect(FlowForkDecisionNodeFlowConnect):
    """Connect Flow to a DecisionNode."""

    fork_node_cls = UML.DecisionNode
    join_node_cls = UML.MergeNode
