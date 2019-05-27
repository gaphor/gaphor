"""
Flow item adapter connections.
"""

from gaphor import UML
from gaphor.diagram.connectors import IConnect, UnaryRelationshipConnect
from gaphor.diagram.actions.action import (
    ActionItem,
    SendSignalActionItem,
    AcceptEventActionItem,
)
from gaphor.diagram.actions.activitynodes import (
    ForkNodeItem,
    ActivityNodeItem,
    DecisionNodeItem,
)
from gaphor.diagram.actions.flow import FlowItem
from gaphor.diagram.actions.objectnode import ObjectNodeItem


class FlowConnect(UnaryRelationshipConnect):
    """
    Connect FlowItem and Action/ObjectNode, initial/final nodes.
    """

    def allow(self, handle, port):
        line = self.line
        subject = self.element.subject

        if (
            handle is line.head
            and isinstance(subject, UML.FinalNode)
            or handle is line.tail
            and isinstance(subject, UML.InitialNode)
        ):
            return None

        return super(FlowConnect, self).allow(handle, port)

    def reconnect(self, handle, port):
        line = self.line
        old_flow = line.subject
        # Secure properties before old_flow is removed:
        name = old_flow.name
        guard_value = old_flow.guard
        self.connect_subject(handle)
        relation = line.subject
        if old_flow:
            relation.name = name
            if guard_value:
                relation.guard = guard_value
            # old_flow.unlink()

    def connect_subject(self, handle):
        line = self.line
        element = self.element

        # TODO: connect opposite side again (in case it's a join/fork or
        #       decision/merge node)
        c1 = self.get_connected(line.head)
        c2 = self.get_connected(line.tail)
        if isinstance(c1, ObjectNodeItem) or isinstance(c2, ObjectNodeItem):
            relation = self.relationship_or_new(
                UML.ObjectFlow, UML.ObjectFlow.source, UML.ObjectFlow.target
            )
        else:
            relation = self.relationship_or_new(
                UML.ControlFlow, UML.ControlFlow.source, UML.ControlFlow.target
            )
        line.subject = relation
        opposite = line.opposite(handle)
        otc = self.get_connected(opposite)
        if opposite and isinstance(otc, (ForkNodeItem, DecisionNodeItem)):
            adapter = IConnect(otc, line)
            adapter.combine_nodes()

    def disconnect_subject(self, handle):
        super(FlowConnect, self).disconnect_subject(handle)
        line = self.line
        opposite = line.opposite(handle)
        otc = self.get_connected(opposite)
        if opposite and isinstance(otc, (ForkNodeItem, DecisionNodeItem)):
            adapter = IConnect(otc, line)
            adapter.decombine_nodes()


IConnect.register(ActionItem, FlowItem)(FlowConnect)
IConnect.register(ActivityNodeItem, FlowItem)(FlowConnect)
IConnect.register(ObjectNodeItem, FlowItem)(FlowConnect)
IConnect.register(SendSignalActionItem, FlowItem)(FlowConnect)
IConnect.register(AcceptEventActionItem, FlowItem)(FlowConnect)


class FlowForkDecisionNodeConnect(FlowConnect):
    """
    Abstract class with common behaviour for Fork/Join node and
    Decision/Merge node.
    """

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

        return super(FlowForkDecisionNodeConnect, self).allow(handle, port)

    def combine_nodes(self):
        """
        Combine join/fork or decision/merge nodes into one diagram item.
        """
        fork_node_cls = self.fork_node_cls
        join_node_cls = self.join_node_cls
        line = self.line
        element = self.element
        subject = element.subject
        if len(subject.incoming) > 1 and len(subject.outgoing) < 2:
            UML.model.swap_element(subject, join_node_cls)
            element.request_update()
        elif len(subject.incoming) < 2 and len(subject.outgoing) > 1:
            UML.model.swap_element(subject, fork_node_cls)
            element.request_update()
        elif (
            not element.combined
            and len(subject.incoming) > 1
            and len(subject.outgoing) > 1
        ):
            join_node = subject

            # determine flow class:
            if [f for f in join_node.incoming if isinstance(f, UML.ObjectFlow)]:
                flow_class = UML.ObjectFlow
            else:
                flow_class = UML.ControlFlow

            UML.model.swap_element(join_node, join_node_cls)
            fork_node = self.element_factory.create(fork_node_cls)
            for flow in list(join_node.outgoing):
                flow.source = fork_node
            flow = self.element_factory.create(flow_class)
            flow.source = join_node
            flow.target = fork_node

            element.combined = fork_node

    def decombine_nodes(self):
        """
        Decombine join/fork or decision/merge nodes.
        """
        fork_node_cls = self.fork_node_cls
        join_node_cls = self.join_node_cls
        line = self.line
        element = self.element
        if element.combined:
            join_node = element.subject
            cflow = join_node.outgoing[0]  # combining flow
            fork_node = cflow.target
            assert fork_node is element.combined
            assert isinstance(join_node, join_node_cls)
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
                    UML.model.swap_element(join_node, fork_node_cls)
                element.combined = None

    def connect_subject(self, handle):
        """
        In addition to a subject connect, the subject of the element may
        be changed.
        For readability, parameters are named after the classes used by
        Join/Fork nodes.
        """
        super(FlowForkDecisionNodeConnect, self).connect_subject(handle)

        # Switch class for self.element Join/Fork depending on the number
        # of incoming/outgoing edges.
        self.combine_nodes()

    def disconnect_subject(self, handle):
        super(FlowForkDecisionNodeConnect, self).disconnect_subject(handle)
        if self.element.combined:
            self.decombine_nodes()


@IConnect.register(ForkNodeItem, FlowItem)
class FlowForkNodeConnect(FlowForkDecisionNodeConnect):
    """Connect Flow to a ForkNode."""

    fork_node_cls = UML.ForkNode
    join_node_cls = UML.JoinNode


@IConnect.register(DecisionNodeItem, FlowItem)
class FlowDecisionNodeConnect(FlowForkDecisionNodeConnect):
    """Connect Flow to a DecisionNode."""

    fork_node_cls = UML.DecisionNode
    join_node_cls = UML.MergeNode
