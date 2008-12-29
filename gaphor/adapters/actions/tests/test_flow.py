"""
Flow item connection adapters tests.
"""

from gaphor.tests import TestCase
from gaphor import UML
from gaphor.diagram import items

class FlowItemBasicNodesConnectionTestCase(TestCase):
    """
    Tests for flow item connecting to basic activity nodes.
    """
    def test_initial_node_glue(self):
        """Test flow item glueing to initial node item
        """
        flow = self.create(items.FlowItem)
        node = self.create(items.InitialNodeItem, UML.InitialNode)

        # tail may not connect to initial node item
        glued = self.glue(flow, flow.tail, node)
        self.assertFalse(glued)

        glued = self.glue(flow, flow.head, node)
        self.assertTrue(glued)


    def test_flow_final_node_glue(self):
        """Test flow item glueing to flow final node item
        """
        flow = self.create(items.FlowItem)
        node = self.create(items.FlowFinalNodeItem, UML.FlowFinalNode)

        # head may not connect to flow final node item
        glued = self.glue(flow, flow.head, node)
        self.assertFalse(glued)

        glued = self.glue(flow, flow.tail, node)
        self.assertTrue(glued)


    def test_activity_final_node_glue(self):
        """Test flow item glueing to activity final node item
        """
        flow = self.create(items.FlowItem)
        node = self.create(items.ActivityFinalNodeItem, UML.ActivityFinalNode)

        # head may not connect to activity final node item
        glued = self.glue(flow, flow.head, node)
        self.assertFalse(glued)

        glued = self.glue(flow, flow.tail, node)
        self.assertTrue(glued)


class FlowItemObjectNodeTestCase(TestCase):
    """
    Flow item connecting to object node item tests.
    """
    def test_glue(self):
        """Test glueing to object node
        """
        flow = self.create(items.FlowItem)
        onode = self.create(items.ObjectNodeItem, UML.ObjectNode)
        glued = self.glue(flow, flow.head, onode)
        self.assertTrue(glued)


    def test_connection(self):
        """Test connection to object node
        """
        flow = self.create(items.FlowItem)
        anode = self.create(items.ActionItem, UML.Action)
        onode = self.create(items.ObjectNodeItem, UML.ObjectNode)

        self.connect(flow, flow.head, anode)
        self.connect(flow, flow.tail, onode)
        self.assertTrue(flow.subject)
        self.assertTrue(isinstance(flow.subject, UML.ObjectFlow))

        self.disconnect(flow, flow.head)
        self.disconnect(flow, flow.tail)

        # opposite connection
        self.connect(flow, flow.head, onode)
        self.connect(flow, flow.tail, anode)
        self.assertTrue(flow.subject)
        self.assertTrue(isinstance(flow.subject, UML.ObjectFlow))


    
class FlowItemActionTestCase(TestCase):
    """
    Flow item connecting to action item tests.
    """
    def test_glue(self):
        """Test flow item glueing to action items
        """
        flow = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, UML.Action)
        a2 = self.create(items.ActionItem, UML.Action)

        glued = self.glue(flow, flow.head, a1)
        self.assertTrue(glued)

        self.connect(flow, flow.head, a1)

        glued = self.glue(flow, flow.tail, a2)
        self.assertTrue(glued)


    def test_connect(self):
        """Test flow item connecting to action items
        """
        flow = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, UML.Action)
        a2 = self.create(items.ActionItem, UML.Action)

        self.connect(flow, flow.head, a1)
        self.connect(flow, flow.tail, a2)

        self.assertTrue(isinstance(flow.subject, UML.ControlFlow))

        self.assertEquals(0, len(a1.subject.incoming))
        self.assertEquals(1, len(a2.subject.incoming))
        self.assertEquals(1, len(a1.subject.outgoing))
        self.assertEquals(0, len(a2.subject.outgoing))

        self.assertTrue(flow.subject in a1.subject.outgoing)
        self.assertTrue(flow.subject.source is a1.subject)
        self.assertTrue(flow.subject in a2.subject.incoming)
        self.assertTrue(flow.subject.target is a2.subject)


    def test_disconnect(self):
        """Test flow item disconnection from action items
        """
        flow = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, UML.Action)
        a2 = self.create(items.ActionItem, UML.Action)

        self.connect(flow, flow.head, a1)
        self.connect(flow, flow.tail, a2)

        self.disconnect(flow, flow.head)
        self.assertTrue(flow.subject is None)
        self.assertEquals(0, len(a1.subject.incoming))
        self.assertEquals(0, len(a2.subject.incoming))
        self.assertEquals(0, len(a1.subject.outgoing))
        self.assertEquals(0, len(a2.subject.outgoing))


class FlowItemDesisionAndForkNodes:
    """
    Base class for flow connecting to decision and fork nodes.
    
    See `FlowItemDecisionNodeTestCase` and `FlowItemForkNodeTestCase` test
    cases.

    Not tested yet

    - If a join node has an incoming object flow, it must have an outgoing
      object flow, otherwise, it must have an outgoing control flow.
    - The edges coming into and out of a fork node must be either all
      object flows or all control flows.
    """

    itemClass = None
    forkNodeClass = None
    joinNodeClass = None

    def test_glue(self):
        """Test decision/fork nodes glue
        """
        flow = self.create(items.FlowItem)
        action = self.create(items.ActionItem, UML.Action)
        node = self.create(self.itemClass, self.joinNodeClass)

        glued = self.glue(flow, flow.head, node)
        self.assertTrue(glued)

        self.connect(flow, flow.head, action)

        glued = self.glue(flow, flow.tail, node)
        self.assertTrue(glued)


    def test_node_class_change(self):
        """ Test node incoming edges

        Connection scheme is presented below::

                  head  tail
            [ a1 ]--flow1-->    |
                             [ jn ] --flow3-->[ a3 ]
            [ a2 ]--flow2-->    |

        Node class changes due to two incoming edges and one outgoing edge.
        """
        flow1 = self.create(items.FlowItem)
        flow2 = self.create(items.FlowItem)
        flow3 = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, UML.Action)
        a2 = self.create(items.ActionItem, UML.Action)
        a3 = self.create(items.ActionItem, UML.Action)
        jn = self.create(self.itemClass, self.joinNodeClass)

        # connect actions first
        self.connect(flow1, flow1.head, a1)
        self.connect(flow2, flow2.head, a2)
        self.connect(flow3, flow3.tail, a2)

        # connect to the node
        self.connect(flow1, flow1.tail, jn)
        self.connect(flow2, flow2.tail, jn)
        self.connect(flow3, flow3.head, jn)

        # node class changes
        self.assertTrue(type(jn.subject) is self.forkNodeClass)


    def test_outgoing_edges(self):
        """Test outgoing edges


        Connection scheme is presented below::

                   head  tail   |--flow2-->[ a2 ]
            [ a1 ] --flow1-->[ jn ]
                                |--flow3-->[ a3 ]
        """
        flow1 = self.create(items.FlowItem)
        flow2 = self.create(items.FlowItem)
        flow3 = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, UML.Action)
        a2 = self.create(items.ActionItem, UML.Action)
        a3 = self.create(items.ActionItem, UML.Action)
        jn = self.create(self.itemClass, self.joinNodeClass)

        # connect actions first
        self.connect(flow1, flow1.head, a1)
        self.connect(flow2, flow2.tail, a2)
        self.connect(flow3, flow3.tail, a2)

        # connect to the node
        self.connect(flow1, flow1.tail, jn)
        self.assertTrue(type(jn.subject) is self.joinNodeClass)

        self.connect(flow2, flow2.head, jn)
        self.assertTrue(type(jn.subject) is self.joinNodeClass)

        self.assertEquals(1, len(jn.subject.incoming))
        self.assertEquals(1, len(jn.subject.outgoing))
        self.assertTrue(flow1.subject in jn.subject.incoming)
        self.assertTrue(flow2.subject in jn.subject.outgoing)

        self.connect(flow3, flow3.head, jn)
        self.assertEquals(2, len(jn.subject.outgoing))

        self.assertTrue(type(jn.subject) is self.forkNodeClass,
                '%s' % jn.subject)


    def test_combined_nodes_connection(self):
        """Test combined nodes

        Connection scheme is presented below::

                   head  tail    |   --flow2--> [ a2 ]
            [ a1 ] --flow1--> [ jn ]
            [ a4 ] --flow4-->    |   --flow3--> [ a3 ]

        Flow `flow4` will force the node to become a combined node.
        """
        flow1 = self.create(items.FlowItem)
        flow2 = self.create(items.FlowItem)
        flow3 = self.create(items.FlowItem)
        flow4 = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, UML.Action)
        a2 = self.create(items.ActionItem, UML.Action)
        a3 = self.create(items.ActionItem, UML.Action)
        a4 = self.create(items.ActionItem, UML.Action)
        jn = self.create(self.itemClass, self.joinNodeClass)

        # connect actions first
        self.connect(flow1, flow1.head, a1)
        self.connect(flow2, flow2.tail, a2)
        self.connect(flow3, flow3.tail, a2)
        self.connect(flow4, flow4.head, a4)

        # connect to the node
        self.connect(flow1, flow1.tail, jn)
        self.connect(flow2, flow2.head, jn)
        self.connect(flow3, flow3.head, jn)

        self.connect(flow4, flow4.tail, jn)
        self.assertTrue(type(jn.subject) is self.joinNodeClass)
        self.assertTrue(jn.combined is not None)

        # check node combination
        self.assertTrue(1, len(jn.subject.outgoing))
        self.assertTrue(1, len(jn.combined.incoming))
        self.assertTrue(jn.subject.outgoing[0] is jn.combined.incoming[0])


    def test_combined_node_disconnection(self):
        """Test combined nodes

        Connection scheme is presented below::

                   head  tail    |   --flow2--> [ a2 ]
            [ a1 ] --flow1--> [ jn ]
            [ a4 ] --flow4-->    |   --flow3--> [ a3 ]

        Flow `flow4` will force the node to become a combined node.
        """

        flow1 = self.create(items.FlowItem)
        flow2 = self.create(items.FlowItem)
        flow3 = self.create(items.FlowItem)
        flow4 = self.create(items.FlowItem)
        a1 = self.create(items.ActionItem, UML.Action)
        a2 = self.create(items.ActionItem, UML.Action)
        a3 = self.create(items.ActionItem, UML.Action)
        a4 = self.create(items.ActionItem, UML.Action)
        jn = self.create(self.itemClass, self.joinNodeClass)

        # connect actions first
        self.connect(flow1, flow1.head, a1)
        self.connect(flow2, flow2.tail, a2)
        self.connect(flow3, flow3.tail, a2)
        self.connect(flow4, flow4.head, a4)

        # connect to the node
        self.connect(flow1, flow1.tail, jn)
        self.connect(flow2, flow2.head, jn)
        self.connect(flow3, flow3.head, jn)
        self.connect(flow4, flow4.tail, jn)

        # needed for test below
        cflow = jn.subject.outgoing[0]
        assert cflow in self.kindof(UML.ControlFlow)

        # test disconnection
        self.disconnect(flow4, flow4.head)
        assert flow4.head.connected_to is None
        self.assertTrue(jn.combined is None)

        flows = self.kindof(UML.ControlFlow)
        self.assertTrue(cflow not in flows, '%s in %s' % (cflow, flows))



class FlowItemForkNodeTestCase(FlowItemDesisionAndForkNodes, TestCase):
    itemClass = items.ForkNodeItem
    forkNodeClass = UML.ForkNode
    joinNodeClass = UML.JoinNode



class FlowItemDecisionNodeTestCase(FlowItemDesisionAndForkNodes, TestCase):
    itemClass = items.DecisionNodeItem
    forkNodeClass = UML.DecisionNode
    joinNodeClass = UML.MergeNode



# vim:sw=4:et:ai
