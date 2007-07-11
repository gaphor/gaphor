# vim:sw=4:et:ai

import unittest
import gaphor.UML as UML
from gaphor.diagram import items
from gaphor.application import Application

class TestActivityNodes(unittest.TestCase):

    def setUp(self):
        Application.init(services=['element_factory'])
        self.element_factory = Application.get_service('element_factory')
        self.diagram = self.element_factory.create(UML.Diagram)

    def shutDown(self):
        Application.shutdown()

    def connectNodes(self, from_node, to_node, flow):
        pass

    def createActionItem(self):
        return self.diagram.create(items.ActionItem, subject=self.element_factory.create(UML.Action))

    def createFlow(self):
        return self.diagram.create(items.FlowItem, subject=self.element_factory.create(UML.ControlFlow))

    def createDecisionNode(self):
        return self.diagram.create(items.DecisionNodeItem, subject=self.element_factory.create(UML.DecisionNode))

    def createObjectNode(self):
        return self.diagram.create(items.ObjectNodeItem, subject=self.element_factory.create(UML.ObjectNode))

    def testMergeNode(self):
        """
        Create decision node UI element and add two incoming flows.
        Element subject should change to MergeNode.
        """

        dnode = self.createDecisionNode()

        assert dnode.subject.__class__ == UML.DecisionNode, 'test problem'

        f1 = self.createFlow()
        f2 = self.createFlow()

        a1 = self.createActionItem()
        a2 = self.createActionItem()

        self.connectNodes(a1, dnode, f1)
        self.connectNodes(a2, dnode, f2)

        self.assertEquals(dnode.subject.__class__, UML.MergeNode)
        self.assertEquals(dnode.props.combined, False)
        # fixme: check that previous subject is destroyed

        self.disconnectNodes(f2)

        self.assertEquals(dnode.subject.__class__, UML.DecisionNode)
        self.assertEquals(dnode.props.combined, False)


    def checkCombinedNode(self, node):
        """
        Check combined UI node element. 

        Return subject of UI node element and combined UML node.
        """
        self.assertEquals(node.props.combined, True)
        self.assertEquals(node.subject.__class__, UML.MergeNode)
        self.assertEquals(len(node.subject.outgoing), 1)
        combined_node = node.subject.outgoing[0].target
        self.assertEquals(combined_node.__class__, UML.DecisionNode)
        self.assertEquals(len(combined_node.incoming), 1)
        return node.subject, combined_node


    def testCombinedNodes(self):
        """
        Test combined nodes.
        """
        dnode = self.createDecisionNode()
        f1 = self.createFlow()
        f2 = self.createFlow()
        f3 = self.createFlow()
        f4 = self.createFlow()

        a1 = self.createActionItem()
        a2 = self.createActionItem()
        a3 = self.createActionItem()
        a4 = self.createActionItem()

        self.connectNodes(a1, dnode, f1)
        self.connectNodes(a2, dnode, f2)

        # merge node created with two incoming flows, not combined yet
        assert dnode.subject.__class__ == UML.MergeNode, 'test problem'

        # connect two more outgoing nodes, node should be combined now
        self.connectNodes(dnode, a3, f3)
        self.connectNodes(dnode, a4, f4)

        n1, n2 = self.checkCombinedNode(dnode)
        # node has two incoming flows: f1, f2
        self.assertEquals(len(n1.incoming), 2)
        self.assert_(f1.subject in n1.incoming)
        self.assert_(f2.subject in n1.incoming)

        # combined node has two outgoing flows: f3, f4
        self.assertEquals(len(n2.outgoing), 2)
        self.assert_(f3.subject in n2.outgoing)
        self.assert_(f4.subject in n2.outgoing)

        # add outgoing flow to combined node
        f5 = self.createFlow()
        a5 = self.createActionItem()
        self.connectNodes(dnode, a5, f5)

        n1, n2 = self.checkCombinedNode(dnode)
        # combined node has new outgoing flow: f5
        self.assertEquals(len(n2.outgoing), 3)
        self.assert_(f5.subject in n2.outgoing)

        # disconnect f5 outgoing flow, node still is combined node
        self.disconnectNodes(f5)
        n1, n2 = self.checkCombinedNode(dnode)
        # f5 is removed from combined node
        self.assertEquals(len(n2.outgoing), 2)
        
        # disconnect outgoing flow, going back to non-combined merge node
        self.disconnectNodes(f4)

        # node should not be combined anymore
        self.assertFalse(dnode.props.combined)

        # f4 was outgoing flow, so UML node should be merge node
        self.assertEqual(dnode.subject.__class__, UML.MergeNode)

        # f3 should be outgoing flow of UML node
        self.assert_(f3.subject in dnode.subject.outgoing)
        # f1 and f2 should be kept as incoming nodes
        self.assert_(f1.subject in dnode.subject.incoming)
        self.assert_(f2.subject in dnode.subject.incoming)

        # combine node again: two incoming flows: f1, f2, two outgoing
        # flows: f3, f4
        f4 = self.createFlow()
        self.connectNodes(dnode, a4, f4)
        n1, n2 = self.checkCombinedNode(dnode)
        self.assert_(f4.subject in n2.outgoing)

        # now, disconnect f1, dnode should be non-combined decision node
        self.disconnectNodes(f1)
        self.assertFalse(dnode.props.combined)
        self.assertEqual(dnode.subject.__class__, UML.DecisionNode)

        assert dnode.subject.__class__ == UML.DecisionNode, 'test problem'

        assert f2.subject and f3.subject and f4.subject, \
            'test problem: f2, f3 and f4 should stay connected'
        assert not f1.subject, 'test problem: f1 should stay disconnected'

        # create combined node from decision node
        self.connectNodes(a1, dnode, f1)
        n1, n2 = self.checkCombinedNode(dnode)
        


    def testCombinedObjectNodes(self):
        """
        Test if combining flow in combined node is object flow when one of
        incoming or outgoing flows is object flow.
        """
        # test for outgoing flows
        dnode = self.createDecisionNode()
        f1 = self.createFlow()
        f2 = self.createFlow()
        f3 = self.createFlow()
        f4 = self.createFlow()

        a1 = self.createActionItem()
        a2 = self.createActionItem()
        a3 = self.createActionItem()
        on = self.createObjectNode()

        self.connectNodes(a1, dnode, f1)
        self.connectNodes(a2, dnode, f2)
        self.connectNodes(dnode, a3, f3)
        self.connectNodes(dnode, on, f4) # f4 is object flow

        n1, n2 = self.checkCombinedNode(dnode)
        # check if combining flow is object flow
        self.assertEquals(n1.outgoing[0].__class__, UML.ObjectFlow)

        # again, but for incoming flows
        dnode = self.createDecisionNode()
        f1 = self.createFlow()
        f2 = self.createFlow()
        f3 = self.createFlow()
        f4 = self.createFlow()

        on = self.createObjectNode()
        a2 = self.createActionItem()
        a3 = self.createActionItem()
        a4 = self.createActionItem()

        self.connectNodes(on, dnode, f1) # f1 is object flow
        self.connectNodes(a2, dnode, f2)
        self.connectNodes(dnode, a3, f3)
        self.connectNodes(dnode, a4, f4)

        n1, n2 = self.checkCombinedNode(dnode)
        # check if combining flow is object flow
        self.assertEquals(n1.outgoing[0].__class__, UML.ObjectFlow)

        f5 = self.createFlow()
        a5 = self.createActionItem()

        self.connectNodes(a5, dnode, f5)

        self.disconnectNodes(f1)

        assert dnode.props.combined, 'test problem'

        # still combined node, combining flow should be control flow
        n1, n2 = self.checkCombinedNode(dnode)
        self.assertEquals(n1.outgoing[0].__class__, UML.ControlFlow)


if __name__ == '__main__':
    unittest.main()
